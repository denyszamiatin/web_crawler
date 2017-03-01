
import re
import urllib.request
import chardet
from bs4 import BeautifulSoup
import collections

price_list = collections.defaultdict(list)

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
    coding = re.search(r'charset[^>, ]*', html)
    coding = coding.group(0).lower()[8:]
    coding = re.search(r'[^\"\'\\/= ].*[^\"\'\\/= ]',coding)
    coding = coding.group(0).lower()
    return coding


def decode_html(encoding, html):
    '''
    use coding name to decode site
    '''
    try:
        return html.decode(encoding)
    except UnicodeDecodeError:
        encoding = guess_encoding_with_chardet(html)
        return html.decode(encoding)


def make_price_list(decoded_site, parent, price='price', name='name'):
    """used on every page"""
    soup = BeautifulSoup(decoded_site, 'html.parser')
    for item in soup.findAll("div", {"class": 'content'}):
        text = item.find("script", {"type": "text/javascript"}).text.strip()
        title_ = re.search(r'title: [^\,]*', text)
        if title_:
            title_ = title_.group(0).lower()[7:].strip()
        price_ = re.search(r'price: [^\,]*', text)
        if price_:
            price_ = price_.group(0).lower()[17:].strip()

        price_list[title_].append(price_)
        print(title_,price_)


def get_links_on_page(new_links, html, site_name):
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup('a')
    for tag in tags:
        url = (tag.get('href', None))
        if url is not None and url.startswith(site_name) \
                and not url.startswith('http://rozetka.com.ua/mobile-phones/') \
                and not url.endswith(('/comments/','/#review','/#promo_video','/credit/','/payments-transfers-travel/',
                                      '/contacts/','/faq/','/#example','/feedback/','/service-centers/','/about/',
                                      '/loyalty/','/salespringgift/','/warranty/','/gift/','/all-categories-goods/',
                                      '/#full_review','/terms/','/jobs/','/partnership/','/newseller/',
                                      '/order-problem/','payments-and-deliveries/','/review')) \
                and not any([(phrase in url) for phrase in ['news-articles-promotions','comments'] ]):
            new_links.add(url)


def find_sub_links(root, site_name):
    '''find links in sites in list "root" '''
    new_links = set()
    for link in root:
        try:
            html = request_url(link)
            get_links_on_page(new_links, html, site_name)
        except ValueError:
            print (root,' cant be opened')
    return new_links


def update_price_list(urls, code, parent_tag):
    '''update price-list with many links'''
    for url in urls:
        print (url)
        try:
            url = validate_url(url)
            html = request_url(url)
            decoded_site = decode_html(code, html)
            make_price_list(decoded_site, parent_tag)
        except AttributeError:
            print (url,'cant be opened' )


#validate_url('www.google.com')
#validate_url('ww.google.com')  # ошибка

#url = validate_url('http://bagsetc.ua/shop/')
url = validate_url('http://rozetka.com.ua/mobile-phones/apple/c80003/v069/')
html = request_url(url)
code = guess_encoding(html)
decoded_site = decode_html(code, html)
make_price_list(decoded_site,None)
print (len(price_list),'price list length')


level_1_depth=find_sub_links({url}, 'http://rozetka.com.ua/')
print ('level_1_depth links ', len(level_1_depth))
update_price_list(level_1_depth,code,'http://rozetka.com.ua/')
print (len(price_list),'price list length')

#level_2_depth=find_sub_links(level_1_depth,'http://rozetka.com.ua/')
#print ('level_2_depth links', len(level_2_depth))
#update_price_list(level_2_depth,code,'http://rozetka.com.ua/')
#print (len(price_list),'price list length')