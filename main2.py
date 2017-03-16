
import re
import urllib.request
import chardet
from bs4 import BeautifulSoup
import collections
import threading
import queue
import sqlite3
from main import Crawler

class Crawler_Rozetka(Crawler):
    def make_price_list(self,decoded_site, parent, price='price', name='name'):
        """used on every page"""
        info_dict=re.search(r'RozetkaStickyGoods_class.prototype.options.goods[^<]*',decoded_site)

        if info_dict:
            info_dict=info_dict.group(0).lower().strip()
            title_ = re.search(r'title: [^\,]*', info_dict)
            if title_:
                title_ = title_.group(0).lower()[8:].strip()
            price_ = re.search(r'price: [^\,]*', info_dict)
            if price_:
                price_ = price_.group(0).lower()[15:].strip()
                price_=int(''.join(price_.split(' '))[1:-1])
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


class Storage:
    def __init__(self,other=None):
        if not other:
            other = 'prices.sqlite'
            self.connection = sqlite3.connect(other)
            self.cursor = self.connection.cursor()
            self.cursor.executescript('''CREATE TABLE Rozetka (
                                         name  TEXT NOT NULL PRIMARY KEY  UNIQUE,
                                         price    INTEGER );
                                      ''')
        else:
            self.connection = sqlite3.connect(other)
            self.cursor = self.connection.cursor()

    def update_sql(self,name,price):
        try:
            self.cursor.execute(''' INSERT INTO Rozetka  (name, price) VALUES (?,?)''',(name,int(price),))
            self.connection.commit()
            print(name,price,'added')
        except sqlite3.IntegrityError:
            print (name,price,' cant be entered, already in db')


crawler=Crawler_Rozetka()

url = crawler.validate_url('http://rozetka.com.ua/mobile-phones/apple/c80003/v069/')
html = crawler.request_url(url)
code = crawler.guess_encoding(html)
decoded_site = crawler.decode_html(code, html)
crawler.make_price_list(decoded_site,None)
print('hi')
print (len(crawler.price_list),'price list length')


level_1_depth=crawler.find_sub_links({url}, 'http://rozetka.com.ua/')
print ('level_1_depth links ', len(level_1_depth))
crawler.multi_update(level_1_depth,code,None)
print (len(crawler.price_list),'price list length')

new_sql_db=Storage(None)                   #use if first time used
#new_sql_db=Storage('prices.sqlite')       #use if second time used

for name,price in crawler.price_list.items():
    new_sql_db.update_sql(name,price[0])

#level_2_depth=crawler.find_sub_links(level_1_depth,'http://rozetka.com.ua/')
#print ('level_2_depth links', len(level_2_depth))
#crawler.multi_update(level_2_depth,code,None)
#print (len(crawler.price_list),'price list length')