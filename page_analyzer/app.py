from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
import page_analyzer.db as db
import validators
import datetime
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route('/')
def index():
    return render_template('index.html', title='Анализатор страниц')


@app.get('/urls')
def get_urls():
    urls = db.get_urls()
    print(urls)
    return render_template('urls.html', urls=urls)


@app.get('/urls/<int:id>')
def show_url(id):
    site, site2 = db.get_queries_for_show_url(id)
    return render_template('show_url.html', site=site, site2=site2)


@app.post('/urls')
def create_url():
    dt = datetime.datetime.now()
    form = request.form.to_dict()
    valid_url = validators.url(form['url'])
    if valid_url and len(form['url']) <= 255:
        id_find = db.get_queries_for_create_url_exist(dt, form)
        if id_find:
            flash('Страница уже существует', 'success')
            return redirect(url_for('show_url', id=id_find[0]))
        id_find = db.get_queries_for_create_url_not_exist(dt, form)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('show_url', id=id_find[0]))
    else:
        flash('Некорректный URL', 'danger')
        return render_template('home.html', title='Анализатор страниц'), 422
