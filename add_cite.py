import re
import urllib
from urllib import request


def add_web_page():
    """
    Works with web-pages started with www. and protocols (http, https)
    """
    while True:
        url = input("Ведите адрес сайта: ")
        url_check = re.match(r'www.|http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                             url)
        if url_check:
            return url
        else:
            print("""Incorrect url! Please, try again.
        Address should start with www., http:// or https://""")


def url_to_html(url):
    '''
    step 2 open web-site
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
            code +=i
    return code


def decode_html(code,html):
    '''
    step 4 use coding name to decode site
    '''
    decoded = html.decode(code)
    return decoded

