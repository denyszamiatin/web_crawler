import re
import urllib.request

URL_PATTERN = re.compile(
    r'www.|http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F]'
    r'[0-9a-fA-F]))+'
)


def validate_url(url):
    """
    Works with web-pages started with www. and protocols (http, https)
    >>> validate_url('www.google.com')
    'www.google.com'
    """
    if URL_PATTERN.match(url) is None:
        raise ValueError('Incorrect url! Please, try again.')
    return url


def request_url(url):
    '''
    Open web-site
    '''
    site = urllib.request.urlopen(url)
    html = site.read()
    return html


def guess_code(html):
    '''
    step 3 take coding type name
    '''
    html = str(html)
    coding = re.search(r'charset[^>, ]*',html)
    coding = coding.group(0).lower()[8:]
    code = ''
    for i in coding:
        if i not in ['/','\\','=',' ','"',"'"]:
            code += i
    return code


def decode_html(code,html):
    '''
    step 4 use coding name to decode site
    '''
    decoded = html.decode(code)
    return decoded

validate_url('www.google.com')
validate_url('ww.google.com')  # ошибка