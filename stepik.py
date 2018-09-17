#!/usr/bin/env python

"""
Basic functions for accessing Stepik API

1. get_stepik_auth
2. token_from_auth
3. *
"""

import os
import requests
import requests.auth


try:
    from ConfigParser import RawConfigParser
except ImportError:
    from configparser import RawConfigParser


STEPIK_API = ''
STEPIK_INI = os.path.expanduser(os.path.join('~', '.stepik', 'creds.ini'))
STEPIK_TOKEN = 'https://stepik.org/oauth2/token/'
STEPIK_COURSE = 'https://stepik.org/api/courses'


def get_stepik_auth(fn, section='langmead-api'):
    config = RawConfigParser(allow_no_value=True)
    if not os.path.exists(fn):
        raise RuntimeError('No such ini file: "%s"' % fn)
    config.read(fn)
    client_id = config.get(section, "client_id")
    client_secret = config.get(section, "client_secret")
    return requests.auth.HTTPBasicAuth(client_id, client_secret)


def token_from_auth(auth):
    response = requests.post(STEPIK_TOKEN,
                             data={'grant_type': 'client_credentials'},
                             auth=auth)
    token = response.json().get('access_token', None)
    if token is None:
        raise RuntimeError('Could not get access token')
    return token


def get_course(course_id, token):
    course = requests.get('%s/%d' % (STEPIK_COURSE, course_id),
                          headers={'Authorization': 'Bearer ' + token}).json()
    if 'detail' in course and course['detail'] == 'Not found':
        raise ValueError('No such course_id: %d' % course_id)
    return course


def go():
    token = token_from_auth(get_stepik_auth(STEPIK_INI))
    course = get_course(32398, token)
    print(course)


if __name__ == '__main__':
    go()
