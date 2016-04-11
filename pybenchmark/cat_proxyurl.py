def fix_url(url):
    """prefix url without http://."""
    if '://' not in url:
        url = 'http://' + url
    return url


def cat_purl(auth,url):
    """concatenate auth info with provided proxy url"""
    url = fix_url(url).split('//')
    caturl = url[0] + '//' + auth + '@' + url[1]
    return caturl

