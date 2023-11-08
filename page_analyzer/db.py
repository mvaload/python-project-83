import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
from psycopg2.extras import NamedTupleCursor

load_dotenv()

DATABASE_USER = os.getenv('POSTGRES_USER')
DATABASE_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
DATABASE_NAME = os.getenv('DATABASE_NAME')
PROVIDER = os.getenv('PROVIDER')
DATABASE_URL = f"{PROVIDER}://{DATABASE_USER}:{DATABASE_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{DATABASE_NAME}"

def connect_to_db():
    return psycopg2.connect(DATABASE_URL)


def get_urls(connect):
    with connect.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute(
            'SELECT * FROM urls ORDER BY id DESC;',
        )
        urls = cursor.fetchall()
    return urls


def get_checks(connect):
    with connect.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute(
            'SELECT DISTINCT ON (url_id) * FROM url_checks ORDER BY url_id DESC, id DESC;',
        )
        checks = cursor.fetchall()
    return checks


def get_urls_with_checks(connect):
    with connect.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute(
            'SELECT * FROM urls ORDER BY id DESC;',
        )
        urls = cursor.fetchall()
        cursor.execute(
            'SELECT DISTINCT ON (url_id) * FROM url_checks ORDER BY url_id DESC, created_at ASC;',
        )
        checks = cursor.fetchall()

    result = []
    checks_by_url_id = {check.url_id: check for check in checks}
    for url in urls:
        url_data = {}
        check = checks_by_url_id.get(url.id)
        url_data['id'] = url.id
        url_data['name'] = url.name
        url_data['last_check_date'] = check.created_at if check else ''
        url_data['status_code'] = check.status_code if check else ''
        result.append(url_data)

    return result


def get_url_by_name(connect, url):
    with connect.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute(
            'SELECT id, name\
            FROM urls\
            WHERE name=%s', (url,),
        )
        url = cursor.fetchone()
    return url


def insert_url(connect, url):
    with connect.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute(
            'INSERT INTO urls (name, created_at)\
            VALUES (%s, %s)\
            RETURNING id;', (url, datetime.now()),
        )
        id = cursor.fetchone().id
    return id


def get_url_by_id(connect, id):
    with connect.cursor(cursor_factory=NamedTupleCursor) as url_cursor:
        url_cursor.execute(
            'SELECT * FROM urls WHERE id = %s', (id,),
        )
        url = url_cursor.fetchone()
    return url


def get_url_checks(connect, id):
    with connect.cursor(cursor_factory=NamedTupleCursor) as check_cursor:
        check_cursor.execute(
            'SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC;', (id,),
        )
        checks = check_cursor.fetchall()
    return checks


def insert_page_check(connect, id, page_data):
    with connect.cursor(cursor_factory=NamedTupleCursor) as check_cursor:
        check_cursor.execute(
            'INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at)\
            VALUES (%s, %s, %s, %s, %s, %s);',
            (id, page_data['status_code'], page_data['h1'], page_data['title'], page_data['description'], datetime.now()),
        )
