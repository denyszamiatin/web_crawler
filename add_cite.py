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
    site=urllib.request.urlopen(url)
    html=site.read()
    return html
