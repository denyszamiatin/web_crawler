
import re
import urllib.request
import chardet
from bs4 import BeautifulSoup

price_list = {}

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


def find_div_by_class(soup, class_):
    return [item.parent for item in soup.findAll("div", {"class": class_})]


def get_valid_parent_name(decoded_site, price='price', name='name'):
    """used only once on first page"""
    soup = BeautifulSoup(decoded_site, "html.parser")
    return [i for i in find_div_by_class(soup, name)
                if i in find_div_by_class(soup, price)][0]['class'][0]


def make_price_list(decoded_site, parent, price='price', name='name'):
    """used on every page"""
    soup = BeautifulSoup(decoded_site, 'html.parser')
    for item in soup.findAll("div", {"class": parent}):
        name_ = item.find("div", {"class": name}).text.strip()
        price_ = item.find("div", {"class": price}).text.strip()
        if name_ not in price_list:
            price_list[name_] = [price_]
        else:
            price_list[name_].append(price_)
        print(name_,price_)

def find_sub_links(root,site_name):
    '''find links in sites in list "root" '''
    new_links=[]
    for link in root:
        try:
            html = urllib.request.urlopen(link).read()
            #decoded_site = decode_html(code, html)
            soup = BeautifulSoup(html,'html.parser')
            tags = soup('a')
            for tag in tags:
                try:
                    url1 = (tag.get('href', None))
                    if url1 not in new_links and url1.startswith(site_name):# and url1 not in links:
                        new_links.append(url1)
                except AttributeError:
                    print(tag,' didnt open')
                    pass
        except ValueError:
            print (root,' cant be opened')
    return new_links

def update_price_list(url_list,code,parent_tag):
    '''update price-list with many links'''
    for i in url_list:
        try:
            url_ = validate_url(i)
            html = request_url(url_)
            decoded_site = decode_html(code, html)
            make_price_list(decoded_site,parent_tag)
        except AttributeError:
            print (i,'cant be opened' )


#validate_url('www.google.com')
#validate_url('ww.google.com')  # ошибка

url = validate_url('http://bagsetc.ua/shop/')
html = request_url(url)
code = guess_encoding(html)
decoded_site = decode_html(code, html)
parent_tag=get_valid_parent_name(decoded_site) #"product-info"
make_price_list(decoded_site,parent_tag)
#print (len(price_list),'price list length')


level_1_depth=find_sub_links([url],url)
print ('level_1_depth links ', len(level_1_depth))
update_price_list(level_1_depth,code,parent_tag)
print (len(price_list),'price list length')

#level_2_depth=find_sub_links(level_1_depth,url)
#update_price_list(level_2_depth,code,parent_tag)
#print ('level_2_depth links', len(level_2_depth))
#print (len(price_list),'price list length')