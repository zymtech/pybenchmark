import gevent
import time
import requests
import sys

from collections import defaultdict, namedtuple
from requests import RequestException
from copy import copy
from gevent.pool import Pool
from parse_cookies import parse_cookies

from pybenchmark.util import resolve_name
from pybenchmark.pgbar import AnimatedProgressBar
from print_info import print_server_info


class RunResults(object):

    """ Using code from Boom,Encapsulates the results of a single run.

    Contains a dictionary of status codes to lists of request durations,
    a list of exception instances raised during the run, the total time
    of the run and an animated progress bar.
    """

    def __init__(self, num=1, quiet=False):
        self.status_code_counter = defaultdict(list)
        self.errors = []
        self.total_time = None
        if num is not None:
            self._progress_bar = AnimatedProgressBar(
                end=num,
                width=65)
        else:
            self._progress_bar = None
        self.quiet = quiet

    def incr(self):
        if self.quiet:
            return
        if self._progress_bar is not None:
            self._progress_bar + 1
            self._progress_bar.show_progress()
        else:
            sys.stdout.write('.')
            sys.stdout.flush()


def onecall(method, url, results, **options):
    """Performs a single HTTP call and puts the result into the
       status_code_counter.

    RequestExceptions are caught and put into the errors set.
    """
    start = time.time()

    if 'data' in options and callable(options['data']):
        options = copy(options)
        options['data'] = options['data'](method, url, options)

    if 'pre_hook' in options:
        method, url, options = options[
            'pre_hook'](method, url, options)
        del options['pre_hook']

    post_hook = lambda _res: _res  # dummy hook
    if 'post_hook' in options:
        post_hook = options['post_hook']
        del options['post_hook']

    try:
        res = post_hook(method(url, **options))
    except RequestException as exc:
        results.errors.append(exc)
    else:
        duration = time.time() - start
        results.status_code_counter[res.status_code].append(duration)
    finally:
        results.incr()


def run(
    url, num=1, duration=None, method='GET', data=None, ct='text/plain',
        auth=None, concurrency=1, cookies=None, timeout=30, headers=None, pre_hook=None, post_hook=None,
        quiet=False):

    if headers is None:
        headers = {}

    if 'content-type' not in headers:
        headers['Content-Type'] = ct

    if data is not None and data.startswith('py:'):
        callable = data[len('py:'):]
        data = resolve_name(callable)

    method = getattr(requests, method.lower())
    options = {'headers': headers}

    if pre_hook is not None:
        options['pre_hook'] = resolve_name(pre_hook)

    if post_hook is not None:
        options['post_hook'] = resolve_name(post_hook)

    if data is not None:
        options['data'] = data

    if auth is not None:
        options['auth'] = tuple(auth.split(':', 1))

    if cookies:
        cookies_dict = parse_cookies(cookies)
    if cookies is not None:
        options['cookies'] = cookies_dict

    options['timeout'] = timeout

    pool = Pool(concurrency)

    start = time.time()
    jobs = None

    res = RunResults(num, quiet)

    try:
        if num is not None:
            jobs = [pool.spawn(onecall, method, url, res, **options)
                    for _ in range(num)]
            pool.join()
        else:
            with gevent.Timeout(duration, False):
                jobs = []
                while True:
                    jobs.append(pool.spawn(onecall, method, url, res,
                                           **options))
                pool.join()
    except KeyboardInterrupt:
        # In case of a keyboard interrupt, just return whatever already got
        # put into the result object.
        pass
    finally:
        res.total_time = time.time() - start

    return res


def load(url, requests, concurrency, duration, method, data, ct, auth, cookies, timeout,
         headers=None, pre_hook=None, post_hook=None, quiet=False, prof=False):
    if not quiet:
        print_server_info(url, method, headers=headers)

        if requests is not None:
            print('Running %d queries - concurrency %d' % (requests,
                                                           concurrency))
        else:
            print('Running for %d seconds - concurrency %d.' %
                  (duration, concurrency))

        sys.stdout.write('Starting the load')
    try:
        if prof:
            import profile, pstats

            pr = profile.Profile()
            d = {
                'run': run,
                'url': url,
                'requests': requests,
                'duration': duration,
                'method': method,
                'data': data,
                'ct': ct,
                'auth': auth,
                'concurrency': concurrency,
                'cookies': cookies,
                'timeout': timeout,
                'headers': headers,
                'pre_hook': pre_hook,
                'post_hook': post_hook,
            }
            pr.runctx('result = run(url, requests, duration, method, data, ct, auth,\
                           concurrency, cookies, timeout, headers, pre_hook, post_hook)', None, d)
            result = d['result']
            pr.dump_stats('profiledata')
            ps = pstats.Stats('profiledata')
            ps.strip_dirs()
            ps.sort_stats('cumulative')
            ps.print_stats()
            return result
        else:
            return run(url, requests, duration, method,
                       data, ct, auth, concurrency, cookies, timeout, headers,
                       pre_hook, post_hook, quiet=quiet)
    finally:
        if not quiet:
            print('Done')
