#! /usr/bin/env python3
""" 
For deployment on ix under CGI.
This code was mostly taken from StackOverflow in order to try to fix a SEVER_NAME KeyError.
Did not work.
"""

import cgitb; cgitb.enable()  # This line enables CGI error reporting
from wsgiref.handlers import CGIHandler
import traceback
import logging

LGGR = logging.getLogger('app.cgi')

import site
site.addsitedir("/home/users/jbayes/public_html/399se/htbin/proj6-Gcal/env/lib/python3.4/site-packages")

app = None
try:
    import meetingmaker
    app = meetingmaker.app
except Exception(e):
    LGGR.info( traceback.format_exc([10]) )
    LGGR.info( 'Problem in cgiappserver-prod with meetingmaker import: %s' % e )

class ScriptNameStripper(object):
   def __init__(self, app):
       self.app = app
   def __call__(self, environ, start_response):
       environ['SCRIPT_NAME'] = ''
       environ['SERVER_NAME'] = 'ix.cs.uoregon.edu'
       return self.app(environ, start_response)

app = ScriptNameStripper(app)

try:
    # CGIHandler().run(app)
    print("Hello, world!")
except Exception(e):
    LGGR.info( traceback.format_exc([10]) )
    LGGR.info( 'Problem in cgiappserver-prod with CGIHandler().run(): %s' % e )