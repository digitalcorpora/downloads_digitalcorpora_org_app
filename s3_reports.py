## BOTTLE VERSION

"""
Generate reports.
"""

import sys
import bottle
from paths import view
from lib.ctools.dbfile import DBMySQL

REPORT_TEMPLATE_FILENAME  = "reports.html"

REPORTS = [
    ('Last 50 corpora uploads ',
     """SELECT s3key, bytes, mtime, tags
        FROM downloadable
        WHERE present=1
        ORDER BY mtime DESC
        LIMIT 50
     """),

    ('DARPA SAFEDOCS and UNSAFEDOCS downloads over past 7 days ',
     """SELECT substr(s3key,1,64) as s3_prefix,
        round(sum(bytes_sent)/max(bytes)) as count, min(dtime) as first,max(dtime) as last
        FROM downloads
        LEFT JOIN downloadable ON downloads.did = downloadable.id
        WHERE s3key like 'corpora/files/CC%%' and dtime > DATE_ADD(NOW(), INTERVAL -7 DAY)
        GROUP BY s3_prefix HAVING count>=1 ORDER BY s3_prefix
     """),

    ('DARPA SAFEDOCS and UNSAFEDOCS downloads over past 30 days ',
     """SELECT substr(s3key,1,64) as s3_prefix,
        round(sum(bytes_sent)/max(bytes)) as count, min(dtime) as first,max(dtime) as last
        FROM downloads
        LEFT JOIN downloadable ON downloads.did = downloadable.id
        WHERE s3key like 'corpora/files/CC%%' and dtime > DATE_ADD(NOW(), INTERVAL -90 DAY)
        GROUP BY s3_prefix HAVING count>=1 ORDER BY s3_prefix
     """),

    ('DARPA SAFEDOCS and UNSAFEDOCS downloads over past 90 days ',
     """SELECT substr(s3key,1,64) as s3_prefix,
        round(sum(bytes_sent)/max(bytes)) as count, min(dtime) as first,max(dtime) as last
        FROM downloads
        LEFT JOIN downloadable ON downloads.did = downloadable.id
        WHERE s3key like 'corpora/files/CC%%' and dtime > DATE_ADD(NOW(), INTERVAL -90 DAY)
        GROUP BY s3_prefix HAVING count>=1 ORDER BY s3_prefix
     """),

    ('Downloads over past 7 days',
     """SELECT s3key, round(sum(bytes_sent)/max(bytes)) as count, min(dtime) as first,max(dtime) as last
        FROM downloads
        LEFT JOIN downloadable ON downloads.did = downloadable.id
        WHERE dtime > DATE_ADD(NOW(), INTERVAL -7 DAY)
        GROUP BY s3key
        HAVING count>=1
        ORDER BY count DESC
     """),

    ('Downloads in the past 24 hours',
     """SELECT s3key, round(sum(bytes_sent)/max(bytes)) as count
        FROM downloads
        LEFT JOIN downloadable ON downloads.did = downloadable.id
        WHERE dtime > addtime(now(),"-24:00:00")
        GROUP BY s3key
        HAVING count>=1
        ORDER BY count DESC
     """),

    ('Failed downloads in past 24 hours',
     """SELECT s3key, round(sum(bytes_sent)/max(bytes)) as count
        FROM downloads
        LEFT JOIN downloadable ON downloads.did = downloadable.id
        WHERE dtime > addtime(now(),"-24:00:00")
        GROUP BY s3key
        HAVING count<1
        ORDER BY count DESC
     """),

    ('Downloads per day for the past 30 days',
     """
     SELECT ddate as `date`, count(*) as count
     FROM (SELECT date(dtime) ddate,s3key,round(sum(bytes_sent)/max(bytes)) as count
           FROM downloads
           LEFT JOIN downloadable ON downloads.did = downloadable.id
           WHERE dtime > DATE_ADD(NOW(), INTERVAL -30 DAY)
     GROUP BY s3key,date(dtime) HAVING count>=1  ) a
     GROUP BY ddate
     """),
]

def report_count():
    return len(REPORTS)

def report_generate(*, auth, num):
    """Run a specific numbered report and return the result as a JSON object that's easy to render.
    :param auth: authorization
    :param num: which report to generate.
    """
    report = REPORTS[int(num)]
    column_names = []
    rows = DBMySQL.csfr(auth, report[1], [], get_column_names=column_names)
    return {'title':report[0],
            'sql':report[1],
            'column_names':column_names,
            'rows': rows}

def reports_json(*, auth, num):
    rdict = report_generate(auth=auth, num=num)
    try:
        colnum = rdict['column_names'].index('s3key')
    except ValueError:
        colnum = -1
    if colnum>=0:
        # Convert from tuples to lists so that we can change the middle value
        rdict['rows'] = [list(row) for row in rdict['rows']]
        for row in rdict['rows']:
            s3key = row[colnum]
            row[colnum] = f'<a href="/{s3key}">{s3key}</a>'
    return rdict

@view(REPORT_TEMPLATE_FILENAME)
def reports_html(*, auth, root=''):
    """If reports with a get, just return the report rendered"""
    try:
        num =  int(bottle.request.params['report'])
    except (TypeError,KeyError,ValueError):
        num = None
    if num is not None:
        rdict = reports_json(num=num, auth=auth)
    else:
        rdict = {}
    rdict['reports'] = [(ct,report[0]) for (ct,report) in enumerate(REPORTS)]
    rdict['sys_version'] = sys.version
    rdict['root'] = root
    return rdict
