# coding = utf-8
import argparse
import sys
import logging

from gevent import monkey
from requests import RequestException
from socket import gaierror

from pybenchmark import __version__
from print_info import print_stats, print_json, print_errors
from loadandrun import load
from resolve_url import resolve
from cat_proxyurl import cat_purl
monkey.patch_all()

logger = logging.getLogger('pybenchmark')

_METHODS = ('GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS')
_DATA_METHODS = ('POST', 'PUT')


def main():
    parser = argparse.ArgumentParser(
        description='For load test, a replacement of Apache Benchmark')
    parser.add_argument(
        '-v', '--version', action='store_true', default=False,
        help='Displays version and exit'
    )
    parser.add_argument('-m', '--method', help='Choose a HTTP method', type=str,
                        default='GET', choices=_METHODS)
    parser.add_argument('--content-type', help='Content-type', type=str, default='text/plain')
    parser.add_argument('-D', '--data', help='DATA', type=str)
    parser.add_argument('-c', '--concurrency', help='Concurrency', type=int, default=1)
    parser.add_argument('-a', '--auth', help='Authentication: username:password', type=str)
    parser.add_argument('--header', help='Custom header', type=str, action='append')
    parser.add_argument('--pre-hook',
                        help=("Python module path (eg: mymodule.pre_hook) "
                              "to a callable which will be executed before "
                              "doing a request for example: "
                              "pre_hook(method, url, options). "
                              "It must return a tupple of parameters given in "
                              "function definition"),
                        type=str)
    parser.add_argument('--post-hook',
                        help=("Python module path (eg: mymodule.post_hook) "
                              "to a callable which will be executed after "
                              "a request is done for example: "
                              "eg. post_hook(response). "
                              "It must return a given response parameter or "
                              "raise an `boom._boom.RequestException` for "
                              "failed request."),
                        type=str)
    parser.add_argument('--json-output',
                        help='Prints the results in JSON instead of the '
                             'default format',
                        action='store_true')
    parser.add_argument('-C', '--cookies', help='''Add cookie, eg.'id=1234'. (repeatable)''',
                        type=str, default=None)
    parser.add_argument('-P', '--proxyauth', help="Add Basic Proxy Authentication, "
                                                  "use a colon to separate username and password",
                        type=str, default=None)
    parser.add_argument('-X', '--proxy', help="Configure proxy, server and port to use",
                        type=str, default=None)
    group0 = parser.add_mutually_exclusive_group()
    group0.add_argument('-q', '--quiet', help="Don't display progress bar",
                        action='store_true')

    group0.add_argument('-p', '--profile', help="Run under the Python profile",
                        action='store_true')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-n', '--requests', help='Number of requests',
                       type=int)

    group.add_argument('-d', '--duration', help='Duration in seconds',
                       type=int)

    parser.add_argument('url', help='URL to hit', nargs='?')
    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)

    if args.url is None:
        print('You need to provide an URL.')
        parser.print_usage()
        sys.exit(0)

    if args.data is not None and args.method not in _DATA_METHODS:
        print("You can't provide data with %r" % args.method)
        parser.print_usage()
        sys.exit(0)

    if args.requests is None and args.duration is None:
        args.requests = 1

    try:
        url, original, resolved = resolve(args.url)
    except gaierror as e:
        print_errors(("DNS resolution failed for %s (%s)" %
                      (args.url, str(e)),))
        sys.exit(1)

    def _split(header):
        header = header.split(':')

        if len(header) != 2:
            print("A header must be of the form name:value")
            parser.print_usage()
            sys.exit(0)

        return header

    if args.header is None:
        headers = {}
    else:
        headers = dict([_split(header) for header in args.header])

    if original != resolved and 'Host' not in headers:
        headers['Host'] = original

    if args.proxyauth:
        if args.proxy:
            args.proxy = cat_purl(args.proxyauth, args.proxy)
        else:
            print("You need to provide proxy info using -X or --proxy")
            sys.exit(0)

    try:
        res = load(
            url, args.requests, args.concurrency, args.duration,
            args.method, args.data, args.content_type, args.auth, args.cookies,
            headers=headers, pre_hook=args.pre_hook,
            post_hook=args.post_hook, quiet=(args.json_output or args.quiet), prof=args.profile)
    except RequestException as e:
        print_errors((e, ))
        sys.exit(1)

    if not args.json_output:
        print_errors(res.errors)
        print_stats(res)
    else:
        print_json(res)

    logger.info('Bye!')


if __name__ == '__main__':
    main()