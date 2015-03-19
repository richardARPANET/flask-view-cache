from __future__ import absolute_import, unicode_literals

import httplib

from flask import Flask, Response, render_template

from flask_view_cache import cache

app = Flask(__name__)
test_app = app.test_client()


@app.route('/')
@cache(expires=60, etag=True)
def hello_world():
    return render_template('template.html')


def test_decorator_adds_headers():
    response = test_app.get('/')

    assert response.status_code == httplib.OK
    assert isinstance(response, Response) is True

    headers = response.headers

    assert 'Expires' in headers.keys()
    assert ('ETag', '3e25960a79dbc69b674cd4ec67a72c62') in headers.items()
    assert ('Cache-Control', 'public, max-age=60') in headers.items()
    assert 'Hello world' == response.data


def test_decorator_returns_304_if_etag_match():
    response = test_app.get(
        '/', headers={'If-None-Match': '3e25960a79dbc69b674cd4ec67a72c62'})

    assert response.status_code == httplib.NOT_MODIFIED
    assert '' == response.data


def test_decorator_returns_data_if_no_etag_match():
    response = test_app.get(
        '/', headers={'If-None-Match': 'this-hash-wont-match'})

    assert response.status_code == httplib.OK
    assert 'Hello world' == response.data


if __name__ == '__main__':
    app.run()
