from meetingmaker import app

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times


#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try: 
        normal = arrow.get( date )
        return normal.format("ddd YYYY-MM-DD")
    except:
        return "(bad date)"

@app.template_filter( 'fmttime' )
def format_arrow_time( time ):
    try:
        normal = arrow.get( time )
        return normal.format("HH:mm")
    except:
        return "(bad time)"

@app.template_filter( 'fmtdatetime' )
def format_arrow_datetime( datetime ):
    try: 
        normal = arrow.get( datetime )
        return normal.format("YYYY-MM-DD HH:mm")
    except:
        return "(bad datetime)"

@app.template_filter( 'humandatetime' )
def human_datetime( datetime ):
    try: 
        normal = arrow.get( datetime )
        return normal.format("ddd MMM D HH:mm")
    except:
        return "(bad datetime)"