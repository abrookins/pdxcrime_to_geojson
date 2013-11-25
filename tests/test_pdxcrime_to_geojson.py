#!/usr/bin/env python
# encoding: utf-8
import json
import unittest

import pdxcrime_to_geojson


class TestConverter(unittest.TestCase):

    def setUp(self):
        self.converter = pdxcrime_to_geojson.Converter()

    def test_converts_row_to_feature(self):
        '''The Converter should convert good data into a Feature'''
        csvRow = ["13807517", "12/01/2011", "01:00:00", "Liquor Laws",
                  "NE WEIDLER ST and NE 1ST AVE PORTLAND, OR 97232", "LLOYD", "PORTLAND PREC NO",
                  "690", 7647471.0160800004, 688344.45013000001]

        expected = {
            "geometry": {
                "coordinates": [-122.66469510763777, 45.53435699129174],
                "type": "Point"
            },
            "id": 13807517,
            "properties": {
                'crimeType': 'Liquor Laws',
                'address': 'NE WEIDLER ST and NE 1ST AVE PORTLAND, OR 97232',
                'neighborhood': 'LLOYD',
                'policePrecinct': 'PORTLAND PREC NO',
                'policeDistrict': 690,
                'reportTime': "2011-12-01T01:00:00"
            },
            "type": "Feature"
        }

        actual = self.converter.convert(csvRow)

        self.assertEqual(json.dumps(expected), actual)

    def test_bad_float_x(self):
        '''The Converter should raise a ConversionError if "X Coordinate" is not floaty'''
        csvRow = ["13807517", "12/01/2011", "01:00:00", "Liquor Laws",
                  "NE WEIDLER ST and NE 1ST AVE PORTLAND, OR 97232", "LLOYD", "PORTLAND PREC NO",
                  "690", "Bad X Coordinate", 688344.45013000001]
        self.assertRaises(pdxcrime_to_geojson.ConversionError, self.converter.convert, csvRow)

    def test_bad_float_y(self):
        '''The Converter should raise a ConversionError if "Y Coordinate" is not floaty'''
        csvRow = ["13807517", "12/01/2011", "01:00:00", "Liquor Laws",
                  "NE WEIDLER ST and NE 1ST AVE PORTLAND, OR 97232", "LLOYD", "PORTLAND PREC NO",
                  "690", 7647471.0160800004, "Bad Y Coordinate"]
        self.assertRaises(pdxcrime_to_geojson.ConversionError, self.converter.convert, csvRow)

    def test_bad_date(self):
        '''The Converter should raise a ConversionError if "Report Date" is not parsable'''
        csvRow = ["13807517", "Bad Date", "01:00:00", "Liquor Laws",
                  "NE WEIDLER ST and NE 1ST AVE PORTLAND, OR 97232", "LLOYD", "PORTLAND PREC NO",
                  "690", 7647471.0160800004, 688344.45013000001]
        self.assertRaises(pdxcrime_to_geojson.ConversionError, self.converter.convert, csvRow)

    def test_bad_time(self):
        '''The Converter should raise a ConversionError if "Report Time" is not parsable'''
        csvRow = ["13807517", "12/01/2011", "Bad Time", "Liquor Laws",
                  "NE WEIDLER ST and NE 1ST AVE PORTLAND, OR 97232", "LLOYD", "PORTLAND PREC NO",
                  "690", 7647471.0160800004, 688344.45013000001]
        self.assertRaises(pdxcrime_to_geojson.ConversionError, self.converter.convert, csvRow)

    def test_convert_all(self):
        '''The Converter should convert a list of CSV rows into a GeoJSON FeatureCollection'''
        csvRows = [
            ["13807517", "12/01/2011", "01:00:00", "Liquor Laws",
             "NE WEIDLER ST and NE 1ST AVE, PORTLAND, OR 97232", "LLOYD", "PORTLAND PREC NO", "690",
             7647471.0160800004, 688344.45013000001],
            ["13716403", "07/07/2011", "18:30:00", "Liquor Laws",
             "NE SCHUYLER ST and NE 1ST AVE, PORTLAND, OR 97212", "ELIOT", "PORTLAND PREC NO",
             "590", 7647488.1558400001, 688869.34843000001]
        ]
        result, skipped = self.converter.convert_all(csvRows)

        expected_skipped = 0
        expected_result = {
            "features": [
                {
                    "geometry": {
                        "coordinates": [
                            -122.66469510763777,
                            45.53435699129174
                        ],
                        "type": "Point"
                    },
                    "id": 13807517,
                    "properties": {
                        "address": "NE WEIDLER ST and NE 1ST AVE, PORTLAND, OR 97232",
                        "crimeType": "Liquor Laws",
                        "neighborhood": "LLOYD",
                        "policeDistrict": 690,
                        "policePrecinct": "PORTLAND PREC NO",
                        "reportTime": "2011-12-01T01:00:00"
                    },
                    "type": "Feature"
                },
                {
                    "geometry": {
                        "coordinates": [
                            -122.66468312170824,
                            45.53579735412487
                        ],
                        "type": "Point"
                    },
                    "id": 13716403,
                    "properties": {
                        "address": "NE SCHUYLER ST and NE 1ST AVE, PORTLAND, OR 97212",
                        "crimeType": "Liquor Laws",
                        "neighborhood": "ELIOT",
                        "policeDistrict": 590,
                        "policePrecinct": "PORTLAND PREC NO",
                        "reportTime": "2011-07-07T18:30:00"
                    },
                    "type": "Feature"
                }
            ],
            "type": "FeatureCollection"
        }

        self.assertEqual(json.dumps(expected_result), result)
        self.assertEqual(expected_skipped, skipped)

    def test_convert_all_skips_bad(self):
        '''The Converter should skip a bad row and report it was skipped'''
        csvRows = [
            ["13807517", "12/01/2011", "01:00:00", "Liquor Laws",
             "NE WEIDLER ST and NE 1ST AVE, PORTLAND, OR 97232", "LLOYD", "PORTLAND PREC NO", "690",
             7647471.0160800004, 688344.45013000001],
            ["13716403", "07/07/2011", "Bad Time", "Liquor Laws",
             "NE SCHUYLER ST and NE 1ST AVE, PORTLAND, OR 97212", "ELIOT", "PORTLAND PREC NO",
             "590", 7647488.1558400001, 688869.34843000001]
        ]
        result, skipped = self.converter.convert_all(csvRows)

        expected_skipped = 1
        expected_result = {
            "features": [
                {
                    "geometry": {
                        "coordinates": [
                            -122.66469510763777,
                            45.53435699129174
                        ],
                        "type": "Point"
                    },
                    "id": 13807517,
                    "properties": {
                        "address": "NE WEIDLER ST and NE 1ST AVE, PORTLAND, OR 97232",
                        "crimeType": "Liquor Laws",
                        "neighborhood": "LLOYD",
                        "policeDistrict": 690,
                        "policePrecinct": "PORTLAND PREC NO",
                        "reportTime": "2011-12-01T01:00:00"
                    },
                    "type": "Feature"
                }
            ],
            "type": "FeatureCollection"
        }

        self.assertEqual(json.dumps(expected_result), result)
        self.assertEqual(expected_skipped, skipped)
