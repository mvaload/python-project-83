import os
import requests
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from dotenv import load_dotenv
from page_analyzer import db
from page_analyzer import parser_html
from page_analyzer import validator

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls_show():
    connect = db.connect_to_db()
    data = db.get_urls_with_checks(connect)
    connect.commit()
    connect.close()

    return render_template(
        'urls/index.html',
        data=data,
    )


@app.post('/urls')
def post_url():
    connect = db.connect_to_db()
    url = request.form['url']
    errors = validator.validate(url)
    if errors:
        for error in errors:
            flash(error, 'danger')
        return render_template('index.html', url_name=url), 422

    normalized_url = validator.normalize(url)
    existed_url = db.get_url_by_name(connect, normalized_url)
    connect.commit()

    if existed_url:
        id = existed_url.id
        flash('Страница уже существует', 'info')
    else:
        id = db.insert_url(connect, normalized_url)
        connect.commit()
        flash('Страница успешно добавлена', 'success')
    connect.close()

    return redirect(url_for('url_show', id=id))


@app.route('/urls/<int:id>')
def url_show(id):
    connect = db.connect_to_db()
    url = db.get_url_by_id(connect, id)
    connect.commit()
    if url is None:
        abort(404)

    url_checks = db.get_url_checks(connect, id)
    connect.commit()

    connect.close()

    return render_template(
        'urls/url.html',
        url=url,
        url_checks=url_checks,
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def url_checks(id):
    connect = db.connect_to_db()
    url = db.get_url_by_id(connect, id)
    connect.commit()

    try:
        response = requests.get(url.name)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_show', id=id))

    page_data = parser_html.get_page_data(response)
    db.insert_page_check(connect, id, page_data)
    connect.commit()
    flash('Страница успешно проверена', 'success')
    connect.close()

    return redirect(url_for('url_show', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
