from flask import Flask, render_template, request
from rozetka_parser import Crawler

# link_laptops = 'http://rozetka.com.ua/notebooks/c80004/filter/'
# link_kids_nutrition = 'http://rozetka.com.ua/detskie-smesi/c2586302/'
link_phones = 'http://rozetka.com.ua/mobile-phones/c80003/preset=smartfon/'

app = Flask(__name__)


@app.route('/')
def index():
    craw = Crawler('http://rozetka.com.ua/mobile-phones/c80003/preset=smartfon/')
    titles = craw.db.select_titles()
    return render_template('index.html', titles=titles)


@app.route('/result', methods=['POST'])
def result():
    select = request.form.get('producer')
    global link_phones
    link_phones = link_phones[:-1] + ';producer={}/'.format(select).lower()  # works only with link_phones
    craw = Crawler(link_phones, main_page=False)
    data = craw.db.select_all_data()
    return render_template('result.html', data=data)

app.run(debug=True)
