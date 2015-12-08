#!/usr/bin/python3

from datetime import datetime

class Event:
    def __init__( self, location="", summary="", description="", dtstart=None, dtend=None ):
        self.location = location
        self.summary = summary
        self.description = description
        self.dtstart = datetime.strptime( dtstart, "%Y-%m-%d-%H-%M" )
        self.dtend = dtend

    def ToICal( self ):
        ret  = "BEGIN:VEVENT\r\n"
        ret += "SUMMARY:" + self.summary + "\r\n"

        if self.dtstart:
            ret += "DTSTART;VALUE=DATE-TIME:" + self.dtstart.strftime( "%Y%m%dT%H%M%S" ) + "\r\n"
        else:
            ret += "DTSTART;VALUE=DATE-TIME:00000000T000000\r\n"

        ret += "LOCATION:" + self.location + "\r\n"
        ret += "END:VEVENT\r\n"
        return ret


class Calendar:    
    def __init__( self ):
        self.eventList = []

    def AddEvent( self, event ):
        self.eventList.append( event )

    def ToICal( self ):
        ret  = "BEGIN:VCALENDAR\r\n"

        for event in self.eventList:
            ret += event.ToICal()

        ret += "END:VCALENDAR\r\n"
        return ret