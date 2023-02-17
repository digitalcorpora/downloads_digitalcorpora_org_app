"""
passenger_wsgi.py script to switch to python3 and use Flask on Dreamhost.

To reload:

$ touch tmp/restart.txt
(or)
$ make touch
"""

import sys
import os
import os.path

DESIRED_PYTHON_VERSION  = '3.9'
DESIRED_PYTHON          = 'python3.9'
DREAMHOST_PYTHON_BINDIR = os.path.join( os.getenv('HOME'), 'opt/python-3.9.2/bin')

debug=False

# Rewrite stderr if not running under pytest
if 'PYTEST' not in os.environ:
    errfile = open( os.path.join( os.getenv('HOME'), 'error.log'),'a')
    os.close(sys.stderr.fileno())
    os.dup2(errfile.fileno(), sys.stderr.fileno())

if sys.version >= DESIRED_PYTHON_VERSION:
    sys.path.append(os.getcwd())
    sys.path.append('app')
    try:
        ## Run Flask application
        from app import app as application    # this is all that is needed
    except ModuleNotFoundError as e:
        print("python interpreter:",sys.executable,file=sys.stderr)
        raise

if DREAMHOST_PYTHON_BINDIR not in os.environ['PATH']:
    if debug:
        sys.stderr.write("Adding "+DREAMHOST_PYTHON_BINDIR+" to PATH\n")
    os.environ['PATH'] = DREAMHOST_PYTHON_BINDIR + ":" + os.environ['PATH']

if (DESIRED_PYTHON not in sys.executable) and ('PYTEST' not in os.environ):
    if debug:
        sys.stderr.write("Executing "+DESIRED_PYTHON+"\n")
    os.execlp(DESIRED_PYTHON, DESIRED_PYTHON, *sys.argv)
