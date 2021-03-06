import flask
from flask import render_template
from flask import request
from flask import url_for
import json

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times

# Modularized Python code
from meetingmaker import app
import meetingmaker.helpers as helpers
import meetingmaker.part2 as part2
from meetingmaker.oauth import *
from meetingmaker.template_filters import *

#############################
#
#  Pages (routed from URLs)
#
#############################

@app.route("/")
@app.route("/index")
def index():
  app.logger.debug("Entering index")
  if 'begin_date' not in flask.session:
    helpers.init_session_values()
  return render_template('index.html')

@app.route("/choose")
def choose():
    ## We'll need authorization to list calendars 
    ## I wanted to put what follows into a function, but had
    ## to pull it back here because the redirect has to be a
    ## 'return' 
    app.logger.debug("Checking credentials for Google calendar access")
    credentials = valid_credentials()
    if not credentials:
      app.logger.debug("Redirecting to authorization")
      return flask.redirect(flask.url_for('oauth2callback'))

    gcal_service = get_gcal_service(credentials)
    app.logger.debug("Returned from get_gcal_service")
    flask.session['calendars'] = helpers.list_calendars(gcal_service)
    return render_template('index.html')

#####
#
#  Option setting:  Buttons or forms that add some
#     information into session state.  Don't do the
#     computation here; use of the information might
#     depend on what other information we have.
#   Setting an option sends us back to the main display
#      page, where we may put the new information to use. 
#
#####

@app.route('/_setrange', methods=['POST'])
def setrange():
    """
    User chose a date and time range with the bootstrap daterange
    and clockpicker widgets.
    """
    app.logger.debug("Entering setrange")

    begin_time = request.form.get('begin_time')
    end_time = request.form.get('end_time')
    flask.session['begin_time'] = helpers.interpret_time(begin_time)
    flask.session['end_time'] = helpers.interpret_time(end_time)

    daterange = request.form.get('daterange')
    flask.flash(helpers.setrange_message(daterange))
    flask.session['daterange'] = daterange

    daterange_parts = daterange.split()
    flask.session['begin_date'] = helpers.interpret_date(daterange_parts[0])
    flask.session['end_date'] = helpers.interpret_date(daterange_parts[2])
    app.logger.debug("Setrange parsed {} - {}  dates as {} - {}".format(
      daterange_parts[0], daterange_parts[1], 
      flask.session['begin_date'], flask.session['end_date']))

    return flask.redirect(flask.url_for("choose"))

@app.route("/_list_events", methods=['POST'])
def _list_events():
  """
  Stashes a session documenting all events in a given date range.
  """
  app.logger.debug("Checking credentials for Google calendar access...")
  credentials = valid_credentials()
  if not credentials:
    app.logger.debug("Redirecting to authorization...")
    return flask.redirect(flask.url_for('oauth2callback'))

  gcal_service = get_gcal_service(credentials)
  app.logger.debug("Returned from get_gcal_service.")

  flask.session['busy_times'] = helpers.busy_times(gcal_service, request.form)

  return flask.redirect(flask.url_for("index"))

@app.route("/_meeting_times", methods=['POST'])
def meeting_times():
  """
  Stashes a session documenting all free times in a given date and time range, based on your Google Calendar.
  """
  app.logger.debug("Checking credentials for Google calendar access...")
  credentials = valid_credentials()
  if not credentials:
    app.logger.debug("Redirecting to authorization...")
    return flask.redirect(flask.url_for('oauth2callback'))

  gcal_service = get_gcal_service(credentials)
  app.logger.debug("Returned from get_gcal_service.")

  ## TODO: Update to windows
  flask.session['windows'] = part2.windows(gcal_service, request.form)

  return flask.redirect(flask.url_for("index"))