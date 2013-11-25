#!/usr/bin/env python
# encoding: utf-8
import logging
import datetime

import geojson
import ogr


log = logging.getLogger(__name__)


class ConversionError(Exception):
    '''An error occurred trying to convert a row.'''
    pass


class Converter(object):
    '''Convert crime data from the City of Portland data to GeoJSON.

    Creates a FeatureCollection of crimes, converting the City's NAD83 coordinates to WGS84.
    '''
    # The default expected headers for CSV rows
    DEFAULT_HEADERS = ["Record ID", "Report Date", "Report Time", "Major Offense Type", "Address",
                       "Neighborhood", "Police Precinct", "Police District", "X Coordinate",
                       "Y Coordinate"]

    def __init__(self, headers=None):
        # State Plane Coordinate System (Oregon North - EPSG:2269, alt: EPSG:2913).
        nad83 = ogr.osr.SpatialReference()
        nad83.ImportFromEPSG(2269)

        # Latitude/longitude (WGS84 - EPSG:4326)
        wgs84 = ogr.osr.SpatialReference()
        wgs84.ImportFromEPSG(4326)

        self.transformation = ogr.osr.CoordinateTransformation(nad83, wgs84)

        headers = headers if headers else self.DEFAULT_HEADERS
        self.headers = {v: k for k, v in enumerate(headers)}

    def get(self, row, header):
        '''A helper to refer to a CSV column index by its name.

        E.g.:
            get(row, 'Record ID')
        '''
        return row[self.headers[header]]

    def fail(self, msg):
        '''Fail with a logged error message ``msg``.

        Raises ConversionError.
        '''
        log.error(msg)
        raise ConversionError(msg)

    def _convert(self, row):
        try:
            x = float(self.get(row, 'X Coordinate'))
            y = float(self.get(row, 'Y Coordinate'))
        except (ValueError, TypeError):
            self.fail('Bad coordinates for row: {}'.format(row))

        coord = self.transformation.TransformPoint(x, y)

        lng = coord[0]
        lat = coord[1]
        date_string = '{} {}'.format(self.get(row, 'Report Date'),
                                     self.get(row, 'Report Time'))

        try:
            date = datetime.datetime.strptime(date_string, '%m/%d/%Y %H:%M:%S')
        except ValueError:
            self.fail('Could not parse date for row: {}'.format(row))

        point = geojson.Point([lng, lat])
        feature = geojson.Feature(geometry=point, id=int(self.get(row, 'Record ID')),
                                  properties={
                                      'crimeType': self.get(row, 'Major Offense Type'),
                                      'address': self.get(row, 'Address'),
                                      'neighborhood': self.get(row, 'Neighborhood'),
                                      'policePrecinct': self.get(row, 'Police Precinct'),
                                      'policeDistrict': int(self.get(row, 'Police District')),
                                      'reportTime': date.isoformat()
                                  })
        return feature

    def convert(self, row):
        '''Convert a row of CSV crime data to a GeoJSON Feature.'''
        feature = self._convert(row)
        return geojson.dumps(feature)

    def convert_all(self, csvRows):
        '''Convert a list of rows of CSV crime data to GeoJSON FeatureCollection'''
        skipped = 0
        features = []
        total = len(csvRows)

        for row in csvRows:
            try:
                features.append(self._convert(row))
            except (ConversionError, ValueError):
                skipped += 1

        if not features:
            raise ValueError('No valid Features found in data')

        collection = geojson.FeatureCollection(features)

        return geojson.dumps(collection), skipped, total
