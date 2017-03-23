
from bs4 import BeautifulSoup as bs
import urllib.request
import sqlite3
import re
import chardet


class Crawler:
    def __init__(self, url, main_page=True):
        self.page = self.get_page(url)
        self.soup = self.cook_soup(self.page)
        self.db = Storage('rozetka_parse.db', main_page)
        if main_page:
            self.get_titles_box()
        else:
            self.get_data()

    def get_titles_box(self):
        data = self.soup.find(class_='filter-parametrs-i')
        if data.get('param') == 'producer':
            self.get_titles(str(data))

    def get_titles(self, data):
        titles = re.findall(r'"eventContent": "(\w+)"', data)
        for title in titles:
            self.db.insert_title(title)

    def get_page(self, url):
        d_page = self.request_url(url)
        charset = self.encode_page(d_page)
        return self.decode_html(charset, d_page)

    @staticmethod
    def cook_soup(page):
        return bs(page, 'html.parser')

    @staticmethod
    def request_url(url):
        site = urllib.request.urlopen(url)
        page = site.read()
        return page

    @staticmethod
    def encode_page(html):
        data = chardet.detect(html)
        return data['encoding']

    @staticmethod
    def decode_html(encoding, page):
        try:
            return page.decode(encoding)
        except UnicodeDecodeError:
            print("error")

    def get_data(self):
        data = self.soup.find("div", "g-i-tile-i-box-desc")
        self.parse_data(data)
        while True:
            try:
                data = data.find_next("div", "g-i-tile-i-box-desc")
                self.parse_data(data)
            except AttributeError:
                break

    def parse_data(self, data):
        title_box = data.find('div', 'g-i-tile-i-title')
        title = title_box.text.strip()
        link = title_box.find('a').get('href')
        img = data.find('img').get('data_src')
        price = str(data.find('script'))
        price = re.split('\n', price)
        price = self.get_pricerawjson(price)
        try:
            price = re.match(r'var pricerawjson = "%7B%22price%22%3A(\d+)', price).group(1)
            self.db.insert_data(title, price, img, link)
        except TypeError:
            print('No items')

    @staticmethod
    def get_pricerawjson(data):
        for el in data:
            if re.search(r'^var pricerawjson', el):
                return el


class Storage:
    def __init__(self, filename, main_page):
        self.conn = sqlite3.connect(filename)
        self.cur = self.conn.cursor()
        if main_page:
            self.cur.execute('''DROP TABLE IF EXISTS Titles''')
            self.cur.execute('''CREATE TABLE Titles(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    title TEXT NOT NULL)
                            ''')
        else:
            self.cur.execute('''DROP TABLE IF EXISTS Rozetka''')
            self.cur.execute('''CREATE TABLE Rozetka(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    title TEXT NOT NULL,
                                    price TEXT NOT NULL,
                                    img   TEXT NOT NULL,
                                    link  TEXT NOT NULL)
                            ''')

    def insert_data(self, title, price, img, link):
        self.cur.execute(''' INSERT INTO Rozetka  (title, price, img, link)
                             VALUES (?,?,?,?)''', (title, price, img, link,))
        self.conn.commit()

    def select_all_data(self):
        self.cur.execute('SELECT title, price, img, link FROM Rozetka')
        return self.cur.fetchall()

    def insert_title(self, title):
        self.cur.execute('''INSERT INTO Titles  (title)
                            VALUES (?)''', (title,))

    def select_titles(self):
        self.cur.execute('SELECT title FROM Titles')
        return self.cur.fetchall()


if __name__ == "__main__":
    Crawler('http://rozetka.com.ua/mobile-phones/apple/c80003/v069/')
