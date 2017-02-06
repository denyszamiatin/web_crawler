import re


def add_web_page(url):
    """
    Works with web-pages started with www. and protocols (http, https)
    """
    pattern = "r'www.|http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'"
    url_check = re.match(pattern, url)
    try:
        if not url_check:
            raise ValueError
        return url
    except ValueError:
        print('Incorrect url! Please, try again.')


add_web_page('www.google.com')
add_web_page('ww.google.com')  # ошибка
