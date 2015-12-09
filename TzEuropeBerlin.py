#!/usr/bin/python3

from datetime import timedelta, datetime, tzinfo

class TzEuropeBerlin(tzinfo):
    def utcoffset( self, dt ):
        return timedelta( hours=1 ) + self.dst( dt )

    def dst( self, dt ):
        # DST starts last Sunday in March
        d = datetime( dt.year, 4, 1 )   # ends last Sunday in October
        self.dston = d - timedelta( days=d.weekday()+1 )
        d = datetime( dt.year, 11, 1 )
        self.dstoff = d - timedelta( days=d.weekday()+1 )
        if self.dston <=  dt.replace( tzinfo=None ) < self.dstoff:
            return timedelta( hours=1 )
        else:
            return timedelta(0)

    def tzname( self, dt ):
         return "Europe/Berlin" 
