#!/usr/bin/env python
# encoding: utf-8
import csv
import os
import sys

from pdxcrime_to_geojson import Converter


def open_file(filename, mode):
    return open(os.path.join(filename), mode)


def convert_file(in_filename, out_filename):
    '''Convert a CSV file of crime data from ``in_filename`` to a GeoJSON file
     of FeatureCollections ``out_filename``.

     Returns the number of rows skipped.
    '''
    if out_filename is None:
        out_filename = '{}.json'.format(in_filename.split('.csv')[0])

    rows = csv.reader(open_file(in_filename, 'r'))
    # Remove the header
    rows = [r for i, r in enumerate(rows) if i > 1]

    converter = Converter()

    try:
        result, skipped, total = converter.convert_all(rows)
    except ValueError:
        print 'Could not find any valid data in the file.'
        return len(rows)

    with open_file(out_filename, 'w') as outfile:
        outfile.write(result)

    return skipped, total


def command():
    '''Entry-point for setup.py'''
    if len(sys.argv) < 2:
        print 'Usage: pdxcrime_to_geojson <csv_filename> <output_json_filename> (optional)'
        return 1

    in_file = sys.argv[1]
    try:
        out_file = sys.argv[2]
    except IndexError:
        out_file = None

    skipped, total = convert_file(in_file, out_file)

    if skipped:
        print 'Result:'
        print '\t{} records original records'.format(total)
        print '\t{} records converted'.format(total - skipped)
        print '\t{} records skipped due to bad data'.format(skipped)


if __name__ == '__main__':
    command()
