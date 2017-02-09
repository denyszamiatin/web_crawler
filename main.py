import re
import urllib.request
import chardet

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


def guess_encoding_with_chardet(html):
    '''
    use if re fails to guess coding type
    '''
    data = chardet.detect(html)
    return data['encoding']


def guess_encoding(html):
    '''
    take coding type name
    '''
    html = str(html)
    coding = re.search(r'charset[^>, ]*', html) # TODO: charset\s*=\s*['"][\\/]{0,3}(.+)['"]
    coding = coding.group(0).lower()[8:]
    encoding = ''
    for i in coding:
        if i not in ['/', '\\', '=', ' ', '"', "'"]:
            encoding += i
    return encoding


def decode_html(encoding, html):
    '''
    use coding name to decode site
    '''
    try:
        return html.decode(encoding)
    except UnicodeDecodeError:
        encoding = guess_encoding_with_chardet(html)
        return html.decode(encoding)


#validate_url('www.google.com')
#validate_url('ww.google.com')  # ошибка


url = validate_url('http://rozetka.com.ua/')            #utf-8
#url = validate_url('http://newspaper.jfdaily.com/')    #gb2312
#url = validate_url('http://news.livedoor.com/')        #euc-jp
html = request_url(url)
code = guess_encoding(html)
decoded_site = decode_html(code, html)
print(code)