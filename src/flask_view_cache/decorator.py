from __future__ import absolute_import, unicode_literals

import datetime
import hashlib
import httplib
import time
from functools import wraps
from wsgiref.handlers import format_date_time

from flask import make_response, request


def _generate_hash(resp):
    hash = hashlib.md5(resp.data)
    return hash.hexdigest()


def cache(expires=None, etag=False):

    def cache_decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            now = datetime.datetime.now()
            resp = make_response(view(*args, **kwargs))

            resp.headers['Last-Modified'] = format_date_time(
                time.mktime(now.timetuple()))

            if expires is None:
                resp.headers['Cache-Control'] = (
                    'no-store, no-cache, must-revalidate, post-check=0, '
                    'pre-check=0, max-age=0')
                resp.headers['Expires'] = '-1'
            else:
                expires_time = now + datetime.timedelta(seconds=expires)

                resp.headers['Cache-Control'] = 'public, max-age={}'.format(
                    expires
                )
                resp.headers['Expires'] = format_date_time(
                    time.mktime(expires_time.timetuple()))

                if etag is True:
                    hashed_data = _generate_hash(resp)
                    resp.headers['ETag'] = hashed_data

                    if_none_match = request.headers.get('If-None-Match')

                    if if_none_match and if_none_match == hashed_data:
                        resp.status = '304 NOT MODIFIED'
                        resp.status_code = httplib.NOT_MODIFIED

            return resp
        return wrapped_view
    return cache_decorator
