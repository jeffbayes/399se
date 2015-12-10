import flask
from flask import render_template
from flask import request
from flask import url_for
import json
import copy
import uuid

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times

# Modularized Python code
# from meetingmaker import app
import meetingmaker.helpers as helpers
# from meetingmaker.oauth import *
# from meetingmaker.template_filters import *

#############################
#
#  Pages (routed from URLs)
#
#############################

def windows(service, form):
  print("Entering windows...")
  ## TODO: Change these to getting them from the form.
  events = [ ]
  not_a_calendar = ["begin_date", "end_date", "begin_time", "end_time"]

  begin_date = arrow.get(form.get('begin_date'))
  end_date = arrow.get(form.get('end_date'))
  begin_time = arrow.get(form.get('begin_time'))
  end_time = arrow.get(form.get('end_time'))

  begin = helpers.replace_time(begin_date, begin_time)
  end = helpers.replace_time(end_date, end_time)

  for calendar in form:
    if calendar in not_a_calendar:
      ## Current mechanic totally sucks, so we have to just exclude these by hand.
      continue
    helpers.extract_events_gcal(events, service, calendar, begin, end)

  windows = meeting_windows(events, begin, end)
  return windows

def meeting_windows(events, begin, end):
  """
  Inputs:
    Array of events (dict containing "event_name" "event_start", "event_end")
    Mash-up begin time (Beginning date and beginning time as one datetime)
    Mash-up end time (Ending date and ending time as one datetime)
  Output:
    
  """
  ## TODO: Ensure dates and times are valid. Maybe put this client-side?
  time_windows = init_time_windows(begin, end)

  mutable_dict = copy.deepcopy(time_windows)
  for event in events:
    time_windows = copy.deepcopy(mutable_dict)
    event_start = event["event_start"]
    event_end = event["event_end"]
    for key in time_windows:
      window = time_windows[key]
      overlap_case = overlap(window, event)
      if overlap_case == (1, 1):
        mutable_dict[key] = (window[0], event_start)
        new_key = str(uuid.uuid4())
        mutable_dict[new_key] = (event_end, window[1])
      elif overlap_case == (2, 1):
        mutable_dict[key] = (event_end, window[1])
      elif overlap_case == (1, 2):
        mutable_dict[key] = (window[0], event_start)
      elif overlap_case == (2, 2):
        del mutable_dict[key]

  time_windows = copy.deepcopy(mutable_dict)
  # for key in time_windows:
  #   ## TODO: Converts dict to list. 
  #   ## Should we sort first?
  #   meeting_windows.append(time_windows[key])

  meeting_windows = sorted(time_windows.values())

  return meeting_windows 


def init_time_windows(start_date, end_date):
  """
  Input:
    start_date, end_date both as arrow objects.
  Output:
    A set of time windows.
  """
  time_windows = {}
  days_in_range = (end_date - start_date).days + 1
  if days_in_range <= 0:
    # Handles error -- bypasses the for loop and returns empty set.
    days_in_range = 0
  end_hour = end_date.hour
  end_minute = end_date.minute

  for i in range(days_in_range):
    ## window_date always inherits the correct start time. Hooray!
    window_start = start_date.replace(days = +i) 
    window_end = window_start.replace(hour = end_hour, minute = end_minute)
    ## Make a date-range tuple.
    window = (window_start.isoformat(), window_end.isoformat())
    key = str(uuid.uuid4())
    time_windows[key] = window

  return time_windows


def overlap(window, event):
  """
  Given a meeting window and an event, finds any overlap and classifies its type.
  Splits window in two:     (1, 1)
  Only clobbers beginning:  (2, 1)
  Only clobbers end:        (1, 2)
  Covers entire window:     (2, 2)
  """
  start_number = 0
  end_number = 0
  if (window[0] < event["event_start"] <= window[1]):
    start_number += 1 ## Event starts inside the window (exclusive)
  if (event["event_start"] <= window[0] <= event["event_end"]):
    start_number += 2 ## Event replaces window beginning.
  if (window[0] <= event["event_end"] < window[1]):
    end_number += 1 ## Event ends within the window (exclusive).
  if (event["event_start"] <= window[1] <= event["event_end"]):
    end_number += 2 ## Event replaces window end.

  case_tuple = (start_number, end_number)
  return case_tuple
