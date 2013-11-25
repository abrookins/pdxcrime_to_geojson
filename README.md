# pdxcrime_to_geojson: Convert Portland crime data to GeoJSON

This package converts a CSV file of crime data from the City of Portland into a
GeoJSON FeatureCollection.

# Installing

Download the package and run `python setup.py install` or `python setup.py develop`.

# Using

    pdxcrime_to_geojson {input_filename} {output_filename}
  
If you omit the output file, the file will be {intput_filename}.json.

# License

MIT.
Copyright Andrew Brookins, 2013.
