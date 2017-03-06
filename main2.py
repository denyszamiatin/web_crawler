
import re
import urllib.request
import chardet
from bs4 import BeautifulSoup
import collections
import threading
import queue
from main import Crawler

class Crawler2(Crawler):
    def make_price_list(self,decoded_site, parent, price='price', name='name'):
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
            with self.lock:
                self.price_list[title_].append(price_)
            print(title_,price_)


    def get_links_on_page(self,new_links, html, site_name):
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


crawler=Crawler2()

url = crawler.validate_url('http://rozetka.com.ua/mobile-phones/apple/c80003/v069/')
html = crawler.request_url(url)
code = crawler.guess_encoding(html)
decoded_site = crawler.decode_html(code, html)
crawler.make_price_list(decoded_site,None)
print (len(crawler.price_list),'price list length')


level_1_depth=crawler.find_sub_links({url}, 'http://rozetka.com.ua/')
print ('level_1_depth links ', len(level_1_depth))
crawler.multi_update(level_1_depth,code,None)
print (len(crawler.price_list),'price list length')

#level_2_depth=crawler.find_sub_links(level_1_depth,'http://rozetka.com.ua/')
#print ('level_2_depth links', len(level_2_depth))
#crawler.multi_update(level_2_depth,code,None)
#print (len(crawler.price_list),'price list length')