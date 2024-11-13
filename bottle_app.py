"""
WSGI file used for bottle interface.

The goal is to only have the bottle code in this file and nowhere else.

Debug:
(cd ~/apps.digitalcorpora.org/;make touch)
https://corp.digitalcorpora.org/
https://corp.digitalcorpora.org/ver
https://corp.digitalcorpora.org/reports

"""

import csv
import json
import sys
import io
import os
import functools
import filetype
from urllib.parse import urlparse

import bottle

import paths
from paths import STATIC_DIR,TEMPLATE_DIR,CREDENTIALS_FILE,view
from lib.ctools import dbfile

import s3_gateway
import s3_reports

assert os.path.exists(TEMPLATE_DIR)

__version__='1.0.0'
VERSION_TEMPLATE='version.txt'

DEFAULT_OFFSET = 0
DEFAULT_ROW_COUNT = 1000000
DEFAULT_SEARCH_ROW_COUNT = 1000

app = bottle.default_app()

@functools.cache
def get_dbreader(fail_gracefully=False):
    """Get the dbreader authentication info from etc/credentials.ini"""
    if 'AWS' in os.environ:
        paths.CREDENTIALS_FILE = paths.CREDENTIALS_FILE.replace('credentials.ini','aws_creds.ini')
    try:
        return dbfile.DBMySQLAuth.FromConfigFile( paths.CREDENTIALS_FILE, 'dbreader' )
    except dbfile.SecretsManagerError as e:
        if fail_gracefully:
            return None
        raise


@bottle.route('/ver')
@view('version.txt')
def func_ver():
    """Demo for reporting python version. Allows us to validate we are using Python3"""
    return {'__version__':__version__,'sys_version':sys.version}

### Local Static
@bottle.get('/static/<path:path>')
def static_path(path):
    kind = filetype.guess(os.path.join(STATIC_DIR,path))
    mimetype = kind.mime if kind else 'text/plain'
    response = bottle.static_file( path, root=STATIC_DIR, mimetype=mimetype )
    response.set_header('Cache-Control', 'public, max-age=5')
    return response

### S3 STATIC
@bottle.route('/robots.txt')
def func_robots():
    """Route https://downloads.digitalcorpora.org/robots.txt which asks Google not to index this."""
    return s3_gateway.s3_app(bucket='digitalcorpora', quoted_prefix='robots.txt', url=bottle.request.url)

## TEMPLATE VIEWS
@bottle.route('/')
@view('index.html')
def func_root():
    o = urlparse(bottle.request.url)
    return {'title':'ROOT',
            'hostname':o.hostname,
            'root':o.path}


@bottle.route('/corpora/')
@bottle.route('/corpora/<path:path>')
def func_corpora_path(path=''):
    """Route https://downloads.digitalcorpora.org/corpora/path"""
    return s3_gateway.s3_app(bucket='digitalcorpora',
                             quoted_prefix='corpora/' + path,
                             auth=get_dbreader(fail_gracefully=True), url=bottle.request.url)

@bottle.route('/downloads/')
@bottle.route('/downloads/<path:path>')
def func_downloads_path(path=''):
    """Route https://downloads.digitalcorpora.org/downloads/path"""
    return s3_gateway.s3_app(bucket='digitalcorpora',
                             quoted_prefix='downloads/' + path,
                             auth=get_dbreader(fail_gracefully=True), url=bottle.request.url)

@bottle.route('/reports')
def reports():
    o = urlparse(bottle.request.url)
    return s3_reports.reports_html(auth=get_dbreader(),root=os.path.dirname(o.path))

@bottle.route('/search')
def search():
    return bottle.jinja2_template('search.html', template_lookup=[TEMPLATE_DIR])

@bottle.route('/index.tsv')
def index_tsf():
    try:
        row_count = int(bottle.request.params['row_count'])
    except (ValueError,KeyError):
        row_count = DEFAULT_ROW_COUNT
    try:
        offset = int(bottle.request.params['offset'])
    except (ValueError,KeyError):
        offset = DEFAULT_OFFSET
    with io.StringIO() as f:
        column_names = []
        rows = dbfile.DBMySQL.csfr(get_dbreader(),
                                   """SELECT * from downloadable WHERE present=1 ORDER BY s3key LIMIT %s, %s""",
                                   (offset,row_count), get_column_names=column_names,asDicts=True)
        writer = csv.DictWriter(f, fieldnames=column_names, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        bottle.response.content_type = "text/plain"
        return f.getvalue()

## API (used by search)

@bottle.route('/search/api')
def search_api():
    q = '%' + bottle.request.params.get('q','') + '%'
    try:
        search_row_count = int(bottle.request.params['row_count'])
    except (ValueError,KeyError):
        search_row_count = DEFAULT_SEARCH_ROW_COUNT
    try:
        offset = int(bottle.request.params['offset'])
    except (ValueError,KeyError):
        offset = DEFAULT_OFFSET
    rows = dbfile.DBMySQL.csfr(get_dbreader(),
                               """SELECT * from downloadable
                                  WHERE s3key LIKE %s AND present=1 ORDER BY s3key LIMIT %s, %s
                               """, (q,offset, search_row_count), asDicts=True)
    return json.dumps(rows,indent=4, sort_keys=True, default=str)
