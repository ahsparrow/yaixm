# Copyright 2017 Alan Sparrow
#
# This file is part of yaixm
#
# yaixm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# yaixm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with yaixm.  If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy
import json as _json
import logging
import math

import jsonschema
import pkg_resources
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

# Load timestamps as strings
def timestamp_constructor(loader, node):
    return loader.construct_scalar(node)

Loader.add_constructor("tag:yaml.org,2002:timestamp", timestamp_constructor)

# Property order for pretty printing (follows order in AIP)
PPRINT_PROP_LIST = [
    "name", "type", "localtype",

    "release", "airspace", "loa",

    "areas",

    "add", "replace",

    "id", "seqno", "upper", "lower", "class", "rules", "boundary",

    "controltype", "geometry",

    "circle", "arc", "line",
    "dir", "radius", "centre", "to",

    "airac_date", "timestamp", "schema_version",

    "notes",
]

# Conversion factor
NM_TO_RADIANS = 1852.0 / 6371000

# Load data from either YAML or JSON
def load(stream, json=False):
    if json:
        if hasattr(stream, 'read'):
            data = _json.load(stream)
        else:
            data = _json.loads(stream)
    else:
        data = yaml.load(stream, Loader=Loader)

    return data

# Check airspace against schema
def validate(yaixm):
    schema = load(pkg_resources.resource_string(__name__, "data/schema.yaml"))

    try:
        jsonschema.validate(yaixm, schema,
                            format_checker=jsonschema.FormatChecker())
    except jsonschema.exceptions.ValidationError as e:
        return e

    return None

# Representer to list properties in fixed order
def ordered_map_representer(dumper, data):
    return dumper.represent_mapping(
            'tag:yaml.org,2002:map',
            sorted(data.items(), key=lambda t: PPRINT_PROP_LIST.index(t[0])))

# Get volume and associated feature for given volume ID
def find_volume(airspace, vid):
    for feature in airspace:
        for volume in feature['geometry']:
            if volume.get('id') == vid:
                return volume, feature

    return None, None

# Merge LoAs into a copy of airspace and return merged copy
def merge_loa(airspace, loas):
    merge_airspace = deepcopy(airspace)

    replace_vol_ids = []
    for loa in loas:
        for area in loa['areas']:
            # Add new LoA airspace features
            merge_airspace.extend(area['add'])

            # Replace volumes in existing features
            for replace_vol in area.get('replace', []):
                # Find volume to be replaced
                volume, feature = find_volume(merge_airspace,
                                              replace_vol['id'])
                if feature is None:
                    continue

                # Delete old volume
                feature['geometry'].remove(volume)

                # Append new volumes (maybe null array)
                feature['geometry'].extend(replace_vol['geometry'])

                # Remove feature if no geometry remaining
                if not feature['geometry']:
                    merge_airspace.remove(feature)

    return merge_airspace

# Split latitude or longitude string into hemisphere, degrees, minutes and
# seconds
def dms(latlon):
    hemi = latlon[-1]
    assert ((hemi in "NS" and len(latlon) == 7) or
            (hemi in "EW" and len(latlon) == 8))

    return {'h': hemi,
            'd': int(latlon[:-5]),
            'm': int(latlon[-5:-3]),
            's': int(latlon[-3:-1])}

# Convert latitude or longitude string to radians
def radians(latlon):
    x = dms(latlon)
    degs = x['d'] + x['m'] / 60.0 + x['s'] / 3600.0
    if x['h'] in "WS":
        degs = -degs

    return math.radians(degs)

# Get (approximate) minimum and maximum latitude for volume, in radians
def minmax_lat(volume):
    lat_arr = []
    for bdry in volume['boundary']:
        if 'circle' in bdry:
            radius = float(bdry['circle']['radius'].split()[0])
            clat = bdry['circle']['centre'].split()[0]
            lat_arr.append(radians(clat) + radius * NM_TO_RADIANS)
            lat_arr.append(radians(clat) - radius * NM_TO_RADIANS)
        elif 'arc' in bdry:
            radius = float(bdry['arc']['radius'].split()[0])
            clat = bdry['arc']['centre'].split()[0]
            lat_arr.append(radians(clat) + radius * NM_TO_RADIANS)
            lat_arr.append(radians(clat) - radius * NM_TO_RADIANS)
        elif 'line' in bdry:
            lat_arr.extend([radians(b.split()[0]) for b in bdry['line']])

    return min(lat_arr), max(lat_arr)
