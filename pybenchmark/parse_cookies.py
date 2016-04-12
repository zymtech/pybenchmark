import re


def parser_cookies(cookies):
    """convert cookies in dict format"""
    # find all matches
    matches = re.findall(r'\w+=[\w.]+',cookies)
    # partition each match at '='
    matches = [m.split('=', 1) for m in matches]
    # use results to make a dict
    return dict(matches)