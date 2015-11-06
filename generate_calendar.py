#!/usr/bin/python3

import argparse
import csv
from datetime import datetime
import os
import os.path
import sys
from icalendar import Calendar, Event, vText


def CheckInput():
    pass


def GenerateEventFromRow( row ):
    event = Event()
    event.add( "summary",  vText( row[0] ) )
    event.add( "location", vText( row[1] ) )
    event.add( "dtstart",  datetime.strptime( row[2], "%Y-%m-%d-%H-%M" ) )
    return event


def GenerateEventsFromFile( filePath, outputCal ):
    try:
        with open( filePath, 'r' ) as csv_file:
            csv_content = csv.reader( csv_file, delimiter=';' )
            for row in csv_content:
                try:
                    outputCal.add_component( GenerateEventFromRow( row ) )
                except:
                    continue
    except:
        pass


def GenerateCalendar( inputPath, outputFilePath ):
    cal = Calendar()

    if os.path.isdir( inputPath ):
        if not inputPath.endswith('/'):
            inputPath += '/'
        ls = os.listdir( inputPath )
        for file_name in ls:
            if file_name.endswith( ".csv" ):
                GenerateEventsFromFile( inputPath + file_name, cal )

    ical_content = cal.to_ical().decode().replace("\r\n", "\n").strip()
    if not ical_content.endswith('\n'):
        ical_content += '\n'

    if outputFilePath == "":
        print( ical_content )
    else:
        with open( outputFilePath, 'w' ) as ical_file:
            ical_file.write( ical_content )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument( "-c", "--check",  help="check the syntax (and write nothing)", action="store_true" )
    parser.add_argument( "-i", "--input",  help="file or folder to read (default: current folder)", default='.' )
    parser.add_argument( "-o", "--output", help="file to write (default: stdout)", default='' )

    args = parser.parse_args()

    if args.check:
        CheckInput()
    else:
        GenerateCalendar( args.input, args.output )
main()
