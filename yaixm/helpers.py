# Copyright 2017 Alan Sparrow
#
# This file is part of yaixm
#
# yaixm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Airplot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with yaixm.  If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy
import json as _json
import logging

import jsonschema
import pkg_resources
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

# Property order for pretty printing (follows order in AIP)
PPRINT_PROP_LIST = [
    "name", "type", "localtype",

    "release", "airspace", "loa",

    "areas",

    "new", "add", "delete",

    "id", "seqno", "upper", "lower", "class", "rules", "boundary",

    "controltype", "geometry",

    "circle", "arc", "line",
    "dir", "radius", "centre", "to",

    "airac_date", "timestamp", "schema_version",

    "notes",
]

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

def find_feature(airspace, id):
    def f_match(id, feature):
        if feature['name'] == id['name']:
            if 'localtype' in id:
                return feature.get('localtype') == id['localtype']
            else:
                return feature['type'] == id.get('type')
        else:
            return False

    match = [f for f in airspace if f_match(id, f)]
    if len(match) > 1:
        logging.warning("Multiple match for %s" % str(id))

    if match:
        return match[0]
    else:
        return None

# Merge LoAs into a copy of airspace and return merged copy
def merge_loa(airspace, loas):
    merge_airspace = deepcopy(airspace)

    delete_vol_ids = []
    for loa in loas:
        for area in loa['areas']:
            # Add new LoA airspace features
            for feature in area['new']:
                merge_airspace.append(feature)

            # Add volumes to existing features
            for add_feature in area.get('add', []):
                # Find feature containing volume to be replaced
                feature = find_feature(merge_airspace, add_feature)
                if feature is None:
                    logging.error("Can't find feature %s" % str(vol_id))
                    continue

                # Append new volumes
                feature['geometry'].extend(add_feature['geometry'])

            # Make list of volumes to be deleted
            delete_vol_ids.extend(area.get('delete', []))

    # Delete volumes (and empty features)
    delete_features = []
    for feature in merge_airspace:
        # Get list of volumes to be removed...
        delete_vols = []
        for vol in feature['geometry']:
            if vol.get('id') in delete_vol_ids:
                delete_vols.append(vol)

        # ... and remove them
        for dv in delete_vols:
            feature['geometry'].remove(dv)

        # If no volumes remaining then add feature to the delete list
        if len(feature['geometry']) == 0:
            delete_features.append(feature)

    for df in delete_features:
        merge_airspace.remove(df)

    return merge_airspace
