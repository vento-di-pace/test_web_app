
# coding=utf-8
import os
import sqlite3
from string import Template
import urllib
from wsgiref.simple_server import make_server
import sys
import re
from cgi import escape

#--------------Logger function--------------------------------------------------
def log(message = u'All is ok! :)', debug=False, severity = 0):
    from sys import argv
    from time import strftime
    from codecs import open

    mode='ab'
    log_file = open(argv[0]+'.log', mode, 'utf-8')
    if not debug:
        print unicode(strftime(u'[%Y-%m-%d] %H:%M:%S>> '))+message
    log_file.write((unicode(strftime(u'[%Y-%m-%d] %H:%M:%S>> '))+u'%s\r\n'%message))#.encode(curr_locale_cp))

    log_file.close()
#-------------End of Logger-----------------------------------------------------

#fields list
fields = ('surname',
        'name',
        'patronymic',
        'region',
        'city',
        'phone',
        'email',
        'comment'
        )
region_filter_threshold = 5
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = 'sqlite.db'

CONNECTION = sqlite3.connect(os.path.join(CURRENT_DIR, DATABASE_NAME))

#check if main table in DB is not exists

tables = CONNECTION.cursor().execute('''
SELECT * FROM sqlite_master WHERE name ="maintable" and type="table";
''')
sys_rows = tables.fetchall()

if not len(sys_rows) == 1:
    CONNECTION.cursor().execute('''
    CREATE TABLE maintable(
       id INTEGER PRIMARY KEY AUTOINCREMENT
       %s
    );
    '''%''.join([',%s TEXT'%field for field in fields]))
    CONNECTION.commit()



def not_found(environ, start_response):
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']


def template_not_found(environ, start_response):
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Template not Found']


# todo list
def index(environ, start_response, saved=False):
    row = CONNECTION.cursor().execute('''
        SELECT id %s
        FROM maintable;
    '''%''.join([',%s'%field for field in fields]))
    comments_qs = row.fetchall()
    CONNECTION.commit()

    comments = u''.join([u'<tr>%s<td><a href="/delete/%s">Удалить</a></td></tr>'%(u''.join([u'<td>%s</td>'%item for item in line]),line[0]) for line in comments_qs])
    try:
        with open('templates/index.html') as template_file:
            template = Template(template_file.read())
    except IOError:
        return template_not_found(environ, start_response)

    start_response('200 OK', [('Content-Type', 'text/html')])
    return [template.substitute({'comments': comments.encode('utf-8'), 'saved': '<div>Ваш комментарий добавлен</div>' if saved else ''})]


# Add comment
def comment(environ, start_response):
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            request_body_size = int(environ['CONTENT_LENGTH'])
            request_body = environ['wsgi.input'].read(request_body_size).split('&')
            print str(request_body)
        except (TypeError, ValueError):
            request_body = []
        else:
            post_values = dict(item.split('=') for item in request_body)
            for field in fields:
                post_values[field] = urllib.unquote_plus(post_values[field])

##            row = CONNECTION.cursor().execute('''
##                INSERT INTO maintable(comment) VALUES("%s");
##            ''' % post_values['comment']

            row = CONNECTION.cursor().execute('''
                INSERT INTO maintable(%s) VALUES("%s");
            ''' % (','.join(fields), '","'.join([post_values[field] for field in fields]))

            )
        return index(environ, start_response, saved=True)
    else:
        try:
            with open('templates/comment.html') as template_file:
                template = Template(template_file.read())
        except IOError:
            return template_not_found(environ, start_response)

        start_response('200 OK', [('Content-Type', 'text/html')])
        return [template.substitute({})]


# Delete comment
def delete(environ, start_response):
    args = environ['url_args']
    if args:
        print args[0]
        CONNECTION.cursor().execute('''
            DELETE FROM maintable WHERE id=%s;
        ''' % args[0])
        CONNECTION.commit()
    return index(environ, start_response)


def stat(environ, start_response):
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            request_body_size = int(environ['CONTENT_LENGTH'])
            request_body = environ['wsgi.input'].read(request_body_size).split('&')
            print str(request_body)
        except (TypeError, ValueError):
            request_body = []
        else:
            post_values = dict(item.split('=') for item in request_body)
            post_values['region'] = urllib.unquote_plus(post_values['region'])


        row = CONNECTION.cursor().execute('''
            SELECT city, COUNT(city)
            FROM maintable GROUP BY city;
        '''%region_filter_threshold)
        comments_qs = row.fetchall()
        CONNECTION.commit()

        comments = u''.join([u'<tr><td>%s</td><td>%s</td></tr>'%(line[0], line[1]) for line in comments_qs])
    else:
        row = CONNECTION.cursor().execute('''
            SELECT region, COUNT(region)
            FROM maintable GROUP BY region HAVING COUNT(region)>%s;
        '''%region_filter_threshold)
        comments_qs = row.fetchall()
        CONNECTION.commit()

        comments = u''.join([u'<tr><td><a name="region" onclick="this.parentNode.submit();return false;">%s</a></td><td>%s</td></tr>'%( line[0], line[1]) for line in comments_qs])

    try:
        with open('templates/index.html') as template_file:
            template = Template(template_file.read())
    except IOError:
        return template_not_found(environ, start_response)

    start_response('200 OK', [('Content-Type', 'text/html')])
    return [template.substitute({'comments': comments.encode('utf-8'), 'saved': ''})]


# Map
urls = [
    (r'^$', index),
    (r'add/?$', comment),
    (r'delete/(.+)$', delete),
    (r'stat/?$', stat),
]


def application(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match is not None:
            environ['url_args'] = match.groups()
            return callback(environ, start_response)
    return not_found(environ, start_response)


if __name__ == '__main__':
    srv = make_server('localhost', 8080, application)
    sys.exit(srv.serve_forever())