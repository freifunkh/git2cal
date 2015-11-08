#!/usr/bin/python3

import argparse
import csv
from datetime import datetime
import os
import os.path
import sys
from icalendar import Calendar, Event, vText
import re


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
                with open( filePath, 'r' ) as csv_file:
                    CheckFileFormat( csv_file )
            except:
                print( "Invalid file: " + filePath, file=sys.stderr )
                return 1
    else:
        try:
            CheckFileFormat( sys.stdin )
        except:
            return 1
    return 0


def FixLineEndings( inp ):
    '''(Hey it's just a helper - I won't document this!)'''
    ret = inp.replace("\r\n", "\n").strip()
    if not ret.endswith('\n'):
        ret += '\n'
    return ret


def GenerateEventFromRow( row ):
    '''Gets a three-element-array and generates an event. Returns the event or throws on error.'''
    event = Event()
    event.add( "summary",  vText( row[0] ) )
    event.add( "location", vText( row[1] ) )
    event.add( "dtstart",  datetime.strptime( row[2], "%Y-%m-%d-%H-%M" ) )
    return event


def GenerateEventsFromFile( csvFile, outputCal ):
    '''Gets a filePath and generates events. Events will be written into outputCal.
    Throws merciless in case of errors.'''
    csv_content = csv.reader( csvFile, delimiter=';' )
    for row in csv_content:
        outputCal.add_component( GenerateEventFromRow( row ) )


def GenerateCalendar( inputPath, outputFilePath ):
    '''Reads the input file and generates an "ical" calendar.
    If inputPath is a folder this function will read all *.csv files from that folder. Current folder is the default.
    If outputFilePath is empty, output will be written to stdout. Otherwise it will be written to file.
    Returns 2 in case of errors, otherwise 0.'''
    try:
        cal = Calendar()

        if inputPath:
            for csv in ListCSVs( inputPath ):
                with open( filePath, 'r' ) as csv_file:
                    GenerateEventsFromFile( csv_file, cal )
        else:
            GenerateEventsFromFile( sys.stdin, cal )

        ical_content = FixLineEndings( cal.to_ical().decode() )
        if outputFilePath == "":
            print( ical_content )
        else:
            with open( outputFilePath, 'w' ) as ical_file:
                ical_file.write( ical_content )

        return 0
    except KeyboardInterrupt:
        return 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument( "-c", "--check",  help="check the syntax (and write nothing)", action="store_true" )
    parser.add_argument( "-i", "--input",  help="file or folder to read (default: current folder)" )
    parser.add_argument( "-o", "--output", help="file to write (default: stdout)", default='' )

    args = parser.parse_args()

    result = 0
    if args.check:
        result = CheckInput( args.input )
    else:
        result = GenerateCalendar( args.input, args.output )

    sys.exit( result )
