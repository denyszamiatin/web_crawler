import re
import urllib.request
import chardet
from bs4 import BeautifulSoup
import collections
import threading
import queue

class Crawler():
    def __init__(self):
        self.q=queue.Queue()
        self.price_list = collections.defaultdict(list)
        self.URL_PATTERN = re.compile(
    r'www.|http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F]'
    r'[0-9a-fA-F]))+'
    )
        self.lock = threading.Lock()

    def validate_url(self,url):
        """
        Works with web-pages started with www. and protocols (http, https)
        >>> validate_url('www.google.com')
        'www.google.com'
        """
        if self.URL_PATTERN.match(url) is None:
            raise ValueError('Incorrect url! Please, try again.')
        return url


    def request_url(self,url):
        '''
        Open web-site
        '''
        site = urllib.request.urlopen(url)
        html = site.read()
        return html


    def guess_encoding_with_chardet(self,html):
        '''
        use if re fails to guess coding type
        '''
        data = chardet.detect(html)
        return data['encoding']


    def guess_encoding(self,html):
        '''
        take coding type name
        '''
        html = str(html)
        coding = re.search(r'charset[^>, ]*', html)
        coding = coding.group(0).lower()[8:]
        coding = re.search(r'[^\"\'\\/= ].*[^\"\'\\/= ]',coding)
        coding = coding.group(0).lower()
        return coding


    def decode_html(self,encoding, html):
        '''
        use coding name to decode site
        '''
        try:
            return html.decode(encoding)
        except UnicodeDecodeError:
            encoding = self.guess_encoding_with_chardet(html)
            return html.decode(encoding)

    def find_div_by_class(self,soup, class_):
        return [item.parent for item in soup.findAll("div", {"class": class_})]

    def get_valid_parent_name(self,decoded_site, price='price', name='name'):
        """used only once on first page"""
        soup = BeautifulSoup(decoded_site, "html.parser")
        return [i for i in self.find_div_by_class(soup, name)
                    if i in self.find_div_by_class(soup, price)][0]['class'][0]

    def make_price_list(self,decoded_site, parent, price='price', name='name'):
        """used on every page"""
        soup = BeautifulSoup(decoded_site, 'html.parser')
        for item in soup.findAll("div", {"class": parent}):
            name_ = item.find("div", {"class": name}).text.strip()
            price_ = item.find("div", {"class": price}).text.strip()
            with self.lock:
                self.price_list[name_].append(price_)
            print(name_,price_)

    def get_links_on_page(self,new_links, html, site_name):
        soup = BeautifulSoup(html, 'html.parser')
        tags = soup('a')
        for tag in tags:
            url = (tag.get('href', None))
            if url is not None and url.startswith(
                    site_name):  # and url1 not in links:
                new_links.add(url)

    def find_sub_links(self,root, site_name):
        '''find links in sites in list "root" '''
        new_links = set()
        for link in root:
            try:
                html = self.request_url(link)
                self.get_links_on_page(new_links, html, site_name)
            except ValueError:
                print (root,' cant be opened')
        return new_links

    def update_price_list(self):
        '''update price-list with many links'''
        while True:
            url, code, parent_tag = self.q.get()
            try:
                url = self.validate_url(url)
                html = self.request_url(url)
                decoded_site = self.decode_html(code, html)
                self.make_price_list(decoded_site, parent_tag)
            except AttributeError:
                print (url,'cant be opened' )
            self.q.task_done()

    def multi_update(self, urls_lis, code, parent_tag):
        threads_num = 2
        for i in range(threads_num):
            t = threading.Thread(target=self.update_price_list)
            t.daemon = True
            t.start()
        for url in urls_lis:
            self.q.put((url,code,parent_tag))
        self.q.join()


#validate_url('www.google.com')
#validate_url('ww.google.com')  # ошибка
if __name__ == '__main__':
    crawler = Crawler()
    url = crawler.validate_url('http://bagsetc.ua/shop/')
    html = crawler.request_url(url)
    code = crawler.guess_encoding(html)
    decoded_site = crawler.decode_html(code, html)
    parent_tag=crawler.get_valid_parent_name(decoded_site) #"product-info"
    crawler.make_price_list(decoded_site,parent_tag)
    print (len(crawler.price_list),'price list length')


    level_1_depth=crawler.find_sub_links({url}, url)
    print ('level_1_depth links ', len(level_1_depth))
    crawler.multi_update(level_1_depth,code,parent_tag)
    print (len(crawler.price_list),'price list length')
    '''
    #level_2_depth=find_sub_links(level_1_depth,url)
    #update_price_list(level_2_depth,code,parent_tag)
    #print ('level_2_depth links', len(level_2_depth))
    #print (len(price_list),'price list length')
    '''