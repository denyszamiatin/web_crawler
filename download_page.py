import urllib.request


def download_page(url):
    """
    function receives full url address and returns byte string which contains html code
    """
    html = urllib.request.urlopen(url)
    return html.read()


test_url = 'https://en.wikinews.org/wiki/Program_Ecumenical_Hellenism_starts_second_decade_of_action'
print(download_page(test_url))
