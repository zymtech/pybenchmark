import urlparse

from requests.packages.urllib3.util import parse_url
from socket import gethostbyname


def resolve(url):
    parts = parse_url(url)

    if not parts.port and parts.scheme == 'https':
        port = 443
    elif not parts.port and parts.scheme == 'http':
        port = 80
    else:
        port = parts.port

    original = parts.host
    resolved = gethostbyname(parts.host)

    # Don't use a resolved hostname for SSL requests otherwise the
    # certificate will not match the IP address (resolved)
    host = resolved if parts.scheme != 'https' else parts.host
    netloc = '%s:%d' % (host, port) if port else host

    return (urlparse.urlunparse((parts.scheme, netloc, parts.path or '',
                                 '', parts.query or '',
                                 parts.fragment or '')),
            original, host)
