import flask
from flask import render_template
from flask import request
from flask import url_for
import json

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times

###
# Globals
###
from meetingmaker import app
from meetingmaker.oauth import *

####
#
#   Initialize session variables 
#
####

def init_session_values():
    """
    Start with some reasonable defaults for date and time ranges.
    Note this must be run in app context ... can't call from main. 
    """
    # Default date span = tomorrow to 1 week from now
    now = arrow.now('local')
    tomorrow = now.replace(days=+1)
    nextweek = now.replace(days=+7)
    flask.session["begin_date"] = tomorrow.floor('day').isoformat()
    flask.session["end_date"] = nextweek.ceil('day').isoformat()
    flask.session["daterange"] = "{} - {}".format(
        tomorrow.format("MM/DD/YYYY"),
        nextweek.format("MM/DD/YYYY"))
    # Default time span each day, 8 to 5
    flask.session["begin_time"] = interpret_time("9am")
    flask.session["end_time"] = interpret_time("5pm")

def interpret_time( text ):
    """
    Read time in a human-compatible format and
    interpret as ISO format with local timezone.
    May throw exception if time can't be interpreted. In that
    case it will also flash a message explaining accepted formats.
    """
    app.logger.debug("Decoding time '{}'".format(text))
    time_formats = ["ha", "h:mma",  "h:mm a", "H:mm"]
    try: 
        as_arrow = arrow.get(text, time_formats).replace(tzinfo=tz.tzlocal())
        app.logger.debug("Succeeded interpreting time")
    except:
        app.logger.debug("Failed to interpret time")
        flask.flash("Time '{}' didn't match accepted formats 13:30 or 1:30pm"
              .format(text))
        raise
    return as_arrow.isoformat()

def interpret_date( text ):
    """
    Convert text of date to ISO format used internally,
    with the local time zone.
    """
    try:
      as_arrow = arrow.get(text, "MM/DD/YYYY").replace(
          tzinfo=tz.tzlocal())
    except:
        flask.flash("Date '{}' didn't fit expected format 12/31/2001")
        raise
    return as_arrow.isoformat()

def next_day(isotext):
    """
    ISO date + 1 day (used in query to Google calendar)
    """
    as_arrow = arrow.get(isotext)
    return as_arrow.replace(days=+1).isoformat()

####
#
#  Functions (NOT pages) that return some information
#
####
  
def list_calendars(service):
    """
    Given a google 'service' object, return a list of
    calendars.  Each calendar is represented by a dict, so that
    it can be stored in the session object and converted to
    json for cookies. The returned list is sorted to have
    the primary calendar first, and selected (that is, displayed in
    Google Calendars web app) calendars before unselected calendars.
    """
    app.logger.debug("Entering list_calendars")
    calendar_list = service.calendarList().list().execute()["items"]
    result = [ ]
    for cal in calendar_list:
        kind = cal["kind"]
        id = cal["id"]
        if "description" in cal: 
            desc = cal["description"]
        else:
            desc = "(no description)"
        summary = cal["summary"]
        # Optional binary attributes with False as default
        selected = ("selected" in cal) and cal["selected"]
        primary = ("primary" in cal) and cal["primary"]
        

        result.append(
          { "kind": kind,
            "id": id,
            "summary": summary,
            "selected": selected,
            "primary": primary
            })
    return sorted(result, key=cal_sort_key)


# def extract_events_gcal(processed_events, service, calendar, begin, end):

#   response = service.events().list(
#     calendarId = calendar,
#     timeMin = begin.datetime.isoformat(), 
#     timeMax = end.datetime.isoformat(),
#     singleEvents = True
#     ).execute()
#   raw_events = response.get('items', [])
#   for event in raw_events:
#     if "transparency" in event:
#       ## We don't want to list transparent events.
#       continue

#     event_name = event['summary']
#     event_start = arrow.get(event['start']['dateTime'])
#     event_end = arrow.get(event['end']['dateTime'])
#     event_details = {
#       "event_name": event_name,
#       "event_start": event_start.format("YYYY-MM-DD HH:mm"),
#       "event_end": event_end.format("YYYY-MM-DD HH:mm")
#     }
#     processed_events.append(event_details)

#   return processed_events


# def busy_times(service, form):
#   busy_times = [ ]
#   not_a_calendar = ["begin_date", "end_date", "begin_time", "end_time"]

#   begin_date = arrow.get(form.get('begin_date'))
#   end_date = arrow.get(form.get('end_date'))
#   begin_time = arrow.get(form.get('begin_time'))
#   end_time = arrow.get(form.get('end_time'))

#   begin = replace_time(begin_date, begin_time)
#   end = replace_time(end_date, end_time)

#   for calendar in form:
#     if calendar in not_a_calendar:
#       ## Current mechanic totally sucks, so we have to just exclude these by hand.
#       continue
#     events_result = service.events().list(
#       calendarId = calendar,
#       timeMin = begin.datetime.isoformat(), 
#       timeMax = end.datetime.isoformat(),
#       singleEvents = True
#       ).execute()

#     events_list = events_result.get('items', [])
#     app.logger.debug(events_list)
#     for event in events_list:
#       if "transparency" in event:
#         ## We don't want to list transparent events.
#         continue

#       event_name = event['summary']
#       event_start = arrow.get(event['start']['dateTime'])
#       event_end = arrow.get(event['end']['dateTime'])
#       valid_event = event_validator(begin, end, event_start, event_end)
#       if valid_event:
#         event_details = {
#           "event_name": event_name,
#           "event_start": event_start.format("YYYY-MM-DD HH:mm"),
#           "event_end": event_end.format("YYYY-MM-DD HH:mm")
#         }
#         busy_times.append(event_details)

#     busy_times.append = extract_events_gcal(service, calendar, begin, end)

#   return busy_times


def extract_events_gcal(processed_events, service, calendar, begin, end):
  response = service.events().list(
    calendarId = calendar,
    timeMin = begin.datetime.isoformat(), 
    timeMax = end.datetime.isoformat(),
    singleEvents = True
    ).execute()
  raw_events = response.get('items', [])
  for event in raw_events:
    if "transparency" in event:
      ## We don't want to list transparent events.
      continue

    event_name = event['summary']
    event_start = arrow.get(event['start']['dateTime'])
    event_end = arrow.get(event['end']['dateTime'])
    event_details = {
      "event_name": event_name,
      "event_start": event_start.isoformat(),
      "event_end": event_end.isoformat()
    }
    processed_events.append(event_details)

  return processed_events


def busy_times(service, form):
  app.logger.debug("Entered busy_times...")
  busy_times = [ ]
  not_a_calendar = ["begin_date", "end_date", "begin_time", "end_time"]

  begin_date = arrow.get(form.get('begin_date'))
  end_date = arrow.get(form.get('end_date'))
  begin_time = arrow.get(form.get('begin_time'))
  end_time = arrow.get(form.get('end_time'))

  begin = replace_time(begin_date, begin_time)
  end = replace_time(end_date, end_time)

  for calendar in form:
    if calendar in not_a_calendar:
      ## Current mechanic totally sucks, so we have to just exclude these by hand.
      continue
    app.logger.debug("Entered calendar in busy_times...")
    app.logger.debug(calendar)

    ## Uses side-effects, appends new events to busy_times.
    extract_events_gcal(busy_times, service, calendar, begin, end)

  return busy_times


def replace_time(date, time):
  """
  Input: 
    date as arrow object.
    time as arrow object.
  Returns:
    datetime as arrow object.
  """
  hour = time.hour
  minute = time.minute
  full_datetime = date.replace(hour = hour, minute = minute)
  return full_datetime

def event_validator(early_time, late_time, event_start, event_end):
  """
  Inputs:
    early_time, late_time: Arrow objects.
    event_start, event_end: Arrow objects.
  Output:
    Boolean - is this a valid event?
  Notes:
    We will never have a date totally out of range, because GCal will parse those out.
    te and tl start with the same date that the event starts on.
  """
  te = event_start.replace(hour = early_time.hour, minute = early_time.minute)
  tl = event_start.replace(hour = late_time.hour, minute = late_time.minute)
  es = event_start.time()
  ee = event_end.time()

  return (early_time < event_start < late_time) or (event_start < early_time < event_end)
  ## TODO: Corner case. Event starts at 11PM and ends at 10AM next day.
  ## That should show up, but will not under this format.

def cal_sort_key( cal ):
    """
    Sort key for the list of calendars:  primary calendar first,
    then other selected calendars, then unselected calendars.
    (" " sorts before "X", and tuples are compared piecewise)
    """
    if cal["selected"]:
       selected_key = " "
    else:
       selected_key = "X"
    if cal["primary"]:
       primary_key = " "
    else:
       primary_key = "X"
    return (primary_key, selected_key, cal["summary"])


def setrange_message(daterange):
    app_message_1 = "OK! Choose the calendars that contain your potential scheduling conflicts. "
    app_message_2 = "We're going to find your busy times between the following dates: "
    formatted_date_range = "{}. ".format(daterange)
    app_message_3 = "If that date range doesn't look right, re-select your date range above and we'll fix it for you."
    return app_message_1 + app_message_2 + formatted_date_range + app_message_3
