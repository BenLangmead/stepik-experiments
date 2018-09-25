#!/usr/bin/env python

"""
Basic functions for accessing Stepik API

1. get_stepik_auth
2. token_from_auth
3. *

Section: collection of lessons, belongs to course
Lesson: collection of steps, belongs to section
Unit: Unit is a lesson within a course -- now I'm really confused
Step: belongs to lesson "basic learning item"

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


def api_url(api):
    return 'https://stepik.org/api/' + api


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


def api_get(func, ident, token):
    item = requests.get('%s/%d' % (api_url(func), ident),
                        headers={'Authorization': 'Bearer ' + token}).json()
    if 'detail' in item and item['detail'] == 'Not found':
        raise ValueError('No such %s id: %d' % (func, item))
    return item


def api_post(func, item, token):
    return requests.post(api_url(func),
                         headers={'Authorization': 'Bearer ' + token},
                         data=item)


def go():
    token = token_from_auth(get_stepik_auth(STEPIK_INI))
    course_id = 32398
    course = api_get('courses', course_id, token)
    course = course['courses'][0]
    for section_id in course['sections']:
        section = api_get('sections', section_id, token)
        section = section['sections'][0]
        assert section['course'] == course_id
        for unit_id in section['units']:
            unit = api_get('units', unit_id, token)
            unit = unit['units'][0]
            assert unit['section'] == section_id
            lesson_id = unit['lesson']
            lesson = api_get('lessons', lesson_id, token)
            lesson = lesson['lessons'][0]
            new_lesson = lesson.copy()
            new_lesson['steps'] = []
            #response = api_post('lessons', new_lesson, token)
            #print(response)
            for step_id in lesson['steps']:
                step = api_get('steps', step_id, token)
                step = step['steps'][0]
                assert step['lesson'] == lesson_id
                #new_step = step.copy()
                #new_step['block']['text'] = u'<div><span>Well well well</span></div>' 
                #response = api_post('steps', new_step, token)
                #print(response)


if __name__ == '__main__':
    go()
