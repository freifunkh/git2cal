#!/usr/bin/env python3

import argparse
import csv
from datetime import datetime, timezone, timedelta
import os
import os.path
import pytz
import sys
import re
import json
import ics


def list_csv_files(input_path):
    '''Yield helper that returns every *.csv file in the given folder.'''
    if os.path.isdir(input_path):
        input_path += '/'
        ls = os.listdir(input_path)
        for file_name in ls:
            if file_name.endswith(".csv"):
                yield input_path + file_name
    else:
        yield input_path


def check_file_format(file_path):
    '''Checks the syntax of a csv file and throws on error.'''
    for line in file_path:
        if not re.fullmatch(".*;.*;[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}\n", line):
            print("Invalid line: " + line, file=sys.stderr)
            raise ValueError


def check_input(input_path):
    '''Checks the syntax of an *.csv file. If a folder is given, it checks all *.csv files in that folder.
    Returns 1 in case of errors, otherwise 0.'''
    if input_path:
        for csv in list_csv_files(input_path):
            try:
                with open(csv, 'r') as csv_file:
                    check_file_format(csv_file)
            except:
                print("Invalid file: " + csv, file=sys.stderr)
                return 1
    else:
        try:
            check_file_format(sys.stdin)
        except:
            return 1
    return 0


def generate_event_from_row(row):
    '''Gets a three-element-array and generates an event. Returns the event. Throws on error.'''
    # TODO: Handle time zones properly
    naive_dt = datetime.strptime(row[2], "%Y-%m-%d-%H-%M")
    timezone = pytz.timezone("Europe/Berlin")
    local_dt = timezone.localize(naive_dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    e = ics.event.Event()
    e.name = row[0]
    e.begin = utc_dt.strftime("%Y%m%dT%H%MZ")
    # TODO: Make duration configurable
    e.duration = timedelta(hours=3)
    e.location = row[1]
    # TODO: Make URL configurable
    e.url = "https://leinelab.org/doku.php/raum:anfahrt"
    e.uid = utc_dt.strftime("event%Y%m%d")
    # TODO: Make description configurable
    e.description = "Freifunk-Treffen im LeineLab. Anfahrt: https://leinelab.org/doku.php/raum:anfahrt"
    return e


def generate_events_from_file(csv_file, output_cal):
    '''Gets a file_path and generates events. Events will be written into output_cal.
    Throws merciless in case of errors.'''
    csv_content = csv.reader(csv_file, delimiter=';')
    for row in csv_content:
        output_cal.events.add(generate_event_from_row(row))


def calendar_to_json(cal):
    '''Generates a JSON string in the same format as our old PHP script. Not pretty but it works.'''
    event_list = []
    c = 0
    for e in sorted(cal.events, key=lambda x: str(x.begin), reverse=True):
        c += 1
        if c > 8:
            break
        line = dict()
        line["label"] = e.location
        line["url"] = "https://hannover.freifunk.net/wiki/Freifunk/Treffen#{}".format(e.location.replace(' ', '_'))

        dt_str = str(e.begin)
        # remove one colon
        dt_str = "{}{}".format(dt_str[0:22], dt_str[23:])
        utc_dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%z")
        # TODO: Handle time zones properly
        timezone = pytz.timezone("Europe/Berlin")
        local_dt = utc_dt.astimezone(timezone)
        offset = local_dt.strftime("%z")
        if len(offset) == 5:
            offset = "{}:{}".format(offset[0:3], offset[3:])
        else:
            offset = ""
        line["date"] = "{}{}".format(local_dt.strftime("%Y-%m-%dT%H:%M:00"), offset)
        event_list.append(line)
    return json.dumps(event_list)


def generate_calendar(input_path, output_file_path, output_format):
    '''Reads the input file and generates an "ical" calendar.
    If input_path is a folder this function will read all *.csv files from that folder. Current folder is the default.
    If output_file_path is empty, output will be written to stdout. Otherwise it will be written to file.
    Returns 2 in case of errors, otherwise 0.'''

    try:
        cal = ics.icalendar.Calendar()

        if input_path:
            for csv in list_csv_files(input_path):
                with open(csv, 'r') as csv_file:
                    generate_events_from_file(csv_file, cal)
        else:
            generate_events_from_file(sys.stdin, cal)

        content = ""
        if output_format == "ics":
            content = str(cal)
        elif output_format == "json":
            content = calendar_to_json(cal)
        else:
            raise ValueError

        if output_file_path == "":
            print(content)
        else:
            with open(output_file_path, 'w') as content_file:
                content_file.write(content)

        return 0
    except KeyboardInterrupt:
        return 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-c", "--check",  help="check the syntax (and write nothing)", action="store_true")
    group.add_argument("-f", "--format", help="the output format",
                       choices=["ics", "json"], default="ics")
    parser.add_argument(
        "-i", "--input",  help="file or folder to read (default: current folder)")
    parser.add_argument(
        "-o", "--output", help="file to write (default: stdout)", default='')

    args = parser.parse_args()

    result = 0
    if args.check:
        result = check_input(args.input)
    else:
        result = generate_calendar(args.input, args.output, args.format)

    sys.exit(result)
