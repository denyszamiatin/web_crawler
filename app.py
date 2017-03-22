from flask import Flask, render_template
from rozetka_parser import Crawler

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result')
def result():
    craw = Crawler('http://rozetka.com.ua/mobile-phones/apple/c80003/v069/')
    data = craw.db.select_all()
    return render_template('result.html', data=data)

app.run()
