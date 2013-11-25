import os

from setuptools import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='pdxcrime_to_geojson',
    description='A script to convert Portland, Oregon crime data to GeoJSON',
    long_description=read('README.md'),
    author='Andrew Brookins',
    author_email='a@andrewbrookins.com',
    url='https://github.com/abrookins/pdxcrime_to_geojson',
    version='0.1',
    packages=['pdxcrime_to_geojson'],
    install_requires=[
        'geojson==1.0.5',
        'GDAL == 1.10.0'
    ],
    entry_points={
        'console_scripts': [
            'pdxcrime_to_geojson = pdxcrime_to_geojson.command:command',
        ]
    }
)