#!/usr/bin/python3

from datetime import datetime, timezone


class Event:
    def __init__(self, location="", summary="", description="", dtstart=None):
        self.location = location
        self.summary = summary
        self.description = description
        self.dtstart = dtstart

    def to_ical(self):
        ret = "BEGIN:VEVENT\r\n"
        ret += "SUMMARY:" + self.summary + "\r\n"

        if self.dtstart:
            ret += "DTSTART;VALUE=DATE-TIME:" + \
                self.dtstart.strftime("%Y%m%dT%H%M%S") + "\r\n"
        else:
            ret += "DTSTART;VALUE=DATE-TIME:00000000T000000\r\n"

        ret += "LOCATION:" + self.location + "\r\n"
        ret += "END:VEVENT\r\n"
        return ret

    def to_dict(self):
        return {"location": self.location, "summary": self.summary, "description": self.description, "dtstart": self.dtstart.strftime("%Y-%m-%dT%H:%M:%S%z")}


class Calendar:
    def __init__(self):
        self.eventList = []

    def _sort(self):
        self.eventList.sort(key=lambda e: e.dtstart.isoformat())

    def add_event(self, event):
        if event:
            self.eventList.append(event)
            return True
        return False

    def to_ical(self):
        self._sort()
        ret = "BEGIN:VCALENDAR\r\n"

        for event in self.eventList:
            ret += event.to_ical()

        ret += "END:VCALENDAR\r\n"
        return ret

    def to_dict(self):
        self._sort()
        return [e.to_dict() for e in self.eventList]
