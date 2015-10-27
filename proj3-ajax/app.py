"""
Very simple Flask web site, with one page
displaying a course schedule.

"""

import flask
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify # For AJAX transactions

import json
import logging

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times

# Our own module
# import acp_limits


###
# Globals
###
app = flask.Flask(__name__)
import CONFIG

import uuid
app.secret_key = str(uuid.uuid4())
app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)


###
# Pages
###

@app.route("/")
@app.route("/index")
@app.route("/calc")
def index():
  app.logger.debug("Main page entry")
  return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] =  flask.url_for("index")
    return flask.render_template('page_not_found.html'), 404


###############
#
# AJAX request handlers 
#   These return JSON, rather than rendering pages. 
#
###############


@app.route("/_calc_times")
def calc_times():
  # Table with speeds. Represented in km, and km/h. Format - (up to this many km): [min speed, max speed].
  speed_table = {200: [15, 34], 400: [15, 32], 600: [15, 30], 1000: [11.428, 28], 1300: [13.333, 26]}
  miles_to_kilometers = 1.60934
  final_controle = ""
  """
  Calculates open/close times from miles, using rules 
  described at http://www.rusa.org/octime_alg.html.
  Expects one URL-encoded argument, the number of miles. 
  """
  app.logger.debug("Got a JSON request");
  distance = request.args.get('distance', 0, type=int)
  brevet_distance = request.args.get('brevet_distance', 0, type=int)
  units = request.args.get('units', 'kilometers', type=str)
  if units == 'miles':
    kilometers = distance * miles_to_kilometers
  else:
    kilometers = distance

  start_date = request.args.get('start_date', "2015/01/01", type=str)
  start_time = request.args.get('start_time', "16:30", type=str)
  app.logger.debug(start_date, ": Start Date")

  # A whole slew of variables. No idea what I'll need or not need yet...
  fmt_start_date = format_arrow_date(start_date)
  fmt_start_time = format_arrow_time(start_time)
  app.logger.debug(fmt_start_time)

  if fmt_start_date == "(bad date)" or fmt_start_time == "(bad time)":
    app.logger.debug("Bad date or bad time.")
    return jsonify(result = "Bad date or time. Retry.")

  full_datetime = fmt_start_date + " " + fmt_start_time
  app.logger.debug(full_datetime)
  arrow_start = arrow.get(full_datetime)


  if kilometers < 0:
    return jsonify(result = "Error: negative controle length.")
  elif kilometers == 0:
    open_hours = 0    ## Special base case.
    close_hours = 1

    arrow_open_time = arrow_start.replace(hours=+open_hours)
    open_time = arrow_open_time.format("YYYY/MM/DD HH:mm")
    arrow_close_time = arrow_start.replace(hours=+close_hours)  
    close_time = arrow_close_time.format("YYYY/MM/DD HH:mm")

    return jsonify(result = open_time + " --> " + close_time + final_controle)


  elif kilometers > brevet_distance:
    if kilometers > (brevet_distance * 1.1):
      return jsonify(result = "Controle is too long for given brevet.")
    final_controle = " (End of Brevet)"
    if brevet_distance == 300:
      speed_calc = 400  # edge case - doesn't have its own speed category
    else:
      speed_calc = brevet_distance
  elif kilometers <= 200:
    speed_calc = 200
  elif kilometers <= 400:
    speed_calc = 400
  elif kilometers <= 600:
    speed_calc = 600
  elif kilometers <= 1000:
    speed_calc = 1000
  elif kilometers <= 1300:
    speed_calc = 1300


  open_hours = kilometers / speed_table[speed_calc][1]
  close_hours = kilometers / speed_table[speed_calc][0]

  arrow_open_time = arrow_start.replace(hours=+open_hours)
  open_time = arrow_open_time.format("MMM D YYYY HH:mm")
  arrow_close_time = arrow_start.replace(hours=+close_hours)  
  close_time = arrow_close_time.format("MMM D YYYY HH:mm")

  return jsonify(result = open_time + "  -->  " + close_time + final_controle)
 
#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try: 
        normal = arrow.get(date, 'YYYY/MM/DD') # lots of formats in case the person is an average user
        app.logger.debug(normal, ": Normal")
        return normal.format("YYYY-MM-DD")
    except:
        return "(bad date)"

@app.template_filter( 'fmttime' )
def format_arrow_time( time ):
    try: 
        normal = arrow.get( time, "HH:mm" )
        app.logger.debug(normal, ": Normal")
        return normal.format("HH:mm")
    except:
        return "(bad time)"



#############


if __name__ == "__main__":
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT)

    
