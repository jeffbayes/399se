import nose
from nose.tools import with_setup
import arrow
import meetingmaker.part2 as part2

## GLOBALS
now = arrow.now()
window_start = now.replace(hour=9, minute=0)
window_end = now.replace(hour=17, minute=0)

def test1():
  ## Cut front chunk from existing window
  expected_begin = now.replace(hour=10, minute=0)
  expected_end = now.replace(hour=17, minute=0)
  expected_answer = [(expected_begin.isoformat(), expected_end.isoformat())]
  event = [{
    "event_name": "TestEvent 2000",
    "event_start": now.replace(hour=8, minute=45).isoformat(),
    "event_end": now.replace(hour=10, minute=0).isoformat()
  }]
  actual_answer = part2.meeting_windows(event, window_start, window_end)
  assert expected_answer == actual_answer

def test2():
  ## Cut back chunk from existing window
  expected_begin = now.replace(hour=9, minute=0)
  expected_end = now.replace(hour=15, minute=45)
  expected_answer = [(expected_begin.isoformat(), expected_end.isoformat())]
  event = [{
    "event_name": "TestEvent 2000",
    "event_start": now.replace(hour=15, minute=45).isoformat(),
    "event_end": now.replace(hour=18, minute=0).isoformat()
  }]
  actual_answer = part2.meeting_windows(event, window_start, window_end)
  assert expected_answer == actual_answer

def test3():
  ## Split existing window with event
  expected_begin1 = now.replace(hour=9, minute=0)
  expected_end1 = now.replace(hour=11, minute=32)

  expected_begin2 = now.replace(hour=12, minute=45)
  expected_end2 = now.replace(hour=17, minute=0)

  expected_answer = [
    (expected_begin1.isoformat(), expected_end1.isoformat()),
    (expected_begin2.isoformat(), expected_end2.isoformat()),
  ]
  event = [{
    "event_name": "TestEvent 2000",
    "event_start": now.replace(hour=11, minute=32).isoformat(),
    "event_end": now.replace(hour=12, minute=45).isoformat()
  }]
  actual_answer = part2.meeting_windows(event, window_start, window_end)
  assert expected_answer == actual_answer

def test4():
  ## Clobber entire window with event
  expected_answer = []
  event = [{
    "event_name": "TestEvent 2000",
    "event_start": now.replace(hour=8, minute=32).isoformat(),
    "event_end": now.replace(hour=18, minute=45).isoformat()
  }]
  actual_answer = part2.meeting_windows(event, window_start, window_end)
  assert expected_answer == actual_answer

def test5():
  ## Event is before window
  expected_begin = now.replace(hour=9, minute=0)
  expected_end = now.replace(hour=17, minute=0)
  expected_answer = [(expected_begin.isoformat(), expected_end.isoformat())]

  event = [{
    "event_name": "TestEvent 2000",
    "event_start": now.replace(hour=6, minute=32).isoformat(),
    "event_end": now.replace(hour=8, minute=45).isoformat()
  }]
  actual_answer = part2.meeting_windows(event, window_start, window_end)
  assert expected_answer == actual_answer

def test6():
  ## Event is after window
  expected_begin = now.replace(hour=9, minute=0)
  expected_end = now.replace(hour=17, minute=0)
  expected_answer = [(expected_begin.isoformat(), expected_end.isoformat())]

  event = [{
    "event_name": "TestEvent 2000",
    "event_start": now.replace(hour=17, minute=32).isoformat(),
    "event_end": now.replace(hour=18, minute=45).isoformat()
  }]
  actual_answer = part2.meeting_windows(event, window_start, window_end)
  assert expected_answer == actual_answer

def test7():
  ## Event is between two windows, overlapping into both days
  local_window_end = window_end.replace(days=+1)
  expected_begin1 = now.replace(hour=9, minute=0)
  expected_end1 = now.replace(hour=17, minute=0)
  expected_begin2 = local_window_end.replace(hour=9, minute=0)
  expected_end2 = local_window_end.replace(hour=17, minute=0)

  expected_answer = [
    (expected_begin1.isoformat(), expected_end1.isoformat()),
    (expected_begin2.isoformat(), expected_end2.isoformat())
  ]

  event = [{
    "event_name": "TestEvent 2000",
    "event_start": now.replace(hour=18, minute=32).isoformat(),
    "event_end": local_window_end.replace(hour=7, minute=45).isoformat()
  }]
  actual_answer = part2.meeting_windows(event, window_start, local_window_end)
  assert expected_answer == actual_answer

def test8():

  ## Event reaches into two windows, overlapping two days.
  local_window_end = window_end.replace(days=+1)
  expected_begin1 = now.replace(hour=9, minute=0)
  expected_end1 = now.replace(hour=15, minute=0)
  expected_begin2 = local_window_end.replace(hour=11, minute=0)
  expected_end2 = local_window_end.replace(hour=17, minute=0)
  expected_answer = [
    (expected_begin1.isoformat(), expected_end1.isoformat()),
    (expected_begin2.isoformat(), expected_end2.isoformat())
  ]

  event = [{
    "event_name": "TestEvent 2000",
    "event_start": now.replace(hour=15, minute=0).isoformat(),
    "event_end": local_window_end.replace(hour=11, minute=0).isoformat()
  }]
  actual_answer = part2.meeting_windows(event, window_start, local_window_end)
  assert expected_answer == actual_answer

def test9():
  ## Event reaches into beginning of second window, doesn't effect first window.
  local_window_end = window_end.replace(days=+1)
  expected_begin1 = now.replace(hour=9, minute=0)
  expected_end1 = now.replace(hour=17, minute=0)
  expected_begin2 = local_window_end.replace(hour=11, minute=0)
  expected_end2 = local_window_end.replace(hour=17, minute=0)
  expected_answer = [
    (expected_begin1.isoformat(), expected_end1.isoformat()),
    (expected_begin2.isoformat(), expected_end2.isoformat())
  ]

  event = [{
    "event_name": "TestEvent 2000",
    "event_start": now.replace(hour=19, minute=0).isoformat(),
    "event_end": local_window_end.replace(hour=11, minute=0).isoformat()
  }]
  actual_answer = part2.meeting_windows(event, window_start, local_window_end)
  assert expected_answer == actual_answer

def test10():
  ## Event cuts off back side of first window, doesn't reach second window.
  local_window_end = window_end.replace(days=+1)
  expected_begin1 = now.replace(hour=9, minute=0)
  expected_end1 = now.replace(hour=15, minute=0)
  expected_begin2 = local_window_end.replace(hour=9, minute=0)
  expected_end2 = local_window_end.replace(hour=17, minute=0)
  expected_answer = [
    (expected_begin1.isoformat(), expected_end1.isoformat()),
    (expected_begin2.isoformat(), expected_end2.isoformat())
  ]

  event = [{
    "event_name": "TestEvent 2000",
    "event_start": now.replace(hour=15, minute=0).isoformat(),
    "event_end": local_window_end.replace(hour=6, minute=0).isoformat()
  }]
  actual_answer = part2.meeting_windows(event, window_start, local_window_end)
  assert expected_answer == actual_answer