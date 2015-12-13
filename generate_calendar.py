#!/usr/bin/python3

import argparse
import csv
from datetime import datetime, timezone, timedelta
import os
import os.path
import sys
import re
import json
import kalle
from TzEuropeBerlin import TzEuropeBerlin

ignore_border_days = 60 # Don't write past events into the calendar.


def ListCSVs( inputPath ):
    '''Yield helper that returns every *.csv file in the given folder.'''
    if os.path.isdir( inputPath ):
        inputPath += '/'
        ls = os.listdir( inputPath )
        for file_name in ls:
            if file_name.endswith( ".csv" ):
                yield inputPath + file_name
    else:
        yield inputPath


def CheckFileFormat( filePath ):
    '''Checks the syntax of a csv file and throws on error.'''
    for line in filePath:
        if not re.fullmatch( ".*;.*;[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}\n", line ):
            print( "Invalid line: " + line, file=sys.stderr )
            raise ValueError


def CheckInput( inputPath ):
    '''Checks the syntax of an *.csv file. If a folder is given, it checks all *.csv files in that folder.
    Returns 1 in case of errors, otherwise 0.'''
    if inputPath:
        for csv in ListCSVs( inputPath ):
            try:
                with open( csv, 'r' ) as csv_file:
                    CheckFileFormat( csv_file )
            except:
                print( "Invalid file: " + csv, file=sys.stderr )
                return 1
    else:
        try:
            CheckFileFormat( sys.stdin )
        except:
            return 1
    return 0


def GenerateEventFromRow( row ):
    '''Gets a three-element-array and generates an event. Returns the event or None, if the event's date is
    far into the past (see ignore_border_days). Throws on error.'''
    global ignore_border_days
    dt = datetime.strptime( row[2], "%Y-%m-%d-%H-%M" )
    now = datetime.now()
    if dt < now - timedelta( days=ignore_border_days ):
        return None
    return kalle.Event( row[1], row[0], dtstart=dt )


def GenerateEventsFromFile( csvFile, outputCal ):
    '''Gets a filePath and generates events. Events will be written into outputCal.
    Throws merciless in case of errors.'''
    csv_content = csv.reader( csvFile, delimiter=';' )
    for row in csv_content:
        outputCal.AddEvent( GenerateEventFromRow( row ) )


def CalendarDictToJSON( calDict ):
    '''Generates a JSON file in the same format as our old PHP script. Not pretty but it works.'''
    for line in calDict:
        dt = datetime.strptime( line["dtstart"], "%Y-%m-%dT%H:%M:%S" )
        dt = dt.replace( tzinfo=TzEuropeBerlin() )
        z = dt.strftime( "%z" )
        line["date"] = dt.strftime( "%Y-%m-%dT%H:%M:%S" ) + z[:3] + ':' + z[3:]

        if line["location"] == "Computerwerkstatt":
            line["url"] = "http://hannover.freifunk.net/wiki/Treffen#Computerwerkstatt_Glocksee"
        elif line["location"] == "Pavillon":
            line["url"] = "http://hannover.freifunk.net/wiki/Treffen#Hannover_Pavillon"

        line["label"] = line["location"]

        delete_list = []
        for key in line:
            if key not in ["date", "label", "url"]:
                delete_list.append( key )
        for key in delete_list:
            del line[key]

    return json.dumps( calDict )


def GenerateCalendar( inputPath, outputFilePath, outputFormat ):
    '''Reads the input file and generates an "ical" calendar.
    If inputPath is a folder this function will read all *.csv files from that folder. Current folder is the default.
    If outputFilePath is empty, output will be written to stdout. Otherwise it will be written to file.
    Returns 2 in case of errors, otherwise 0.'''

    try:
        cal = kalle.Calendar()

        if inputPath:
            for csv in ListCSVs( inputPath ):
                with open( csv, 'r' ) as csv_file:
                    GenerateEventsFromFile( csv_file, cal )
        else:
            GenerateEventsFromFile( sys.stdin, cal )

        content = ""
        if   outputFormat == "ics":
            content = cal.ToICal()
        elif outputFormat == "json":
            content = CalendarDictToJSON( cal.ToDict() )
        else:
            raise ValueError

        if outputFilePath == "":
            print( content )
        else:
            with open( outputFilePath, 'w' ) as content_file:
                content_file.write( content )

        return 0
    except KeyboardInterrupt:
        return 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument(  "-c", "--check",  help="check the syntax (and write nothing)", action="store_true" )
    group.add_argument(  "-f", "--format", help="the output format", choices=["ics", "json"], default="ics" )
    parser.add_argument( "-i", "--input",  help="file or folder to read (default: current folder)" )
    parser.add_argument( "-o", "--output", help="file to write (default: stdout)", default='' )

    args = parser.parse_args()

    result = 0
    if args.check:
        result = CheckInput( args.input )
    else:
        result = GenerateCalendar( args.input, args.output, args.format )

    sys.exit( result )
