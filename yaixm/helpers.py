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

    "feature", "mods",
    "volume_id",

    "seqno", "upper", "lower", "class", "rules", "boundary",

    "controltype", "geometry",

    "circle", "arc", "line",
    "dir", "radius", "centre", "to",

    "notes"
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
def validate(yaxim):
    schema = load(pkg_resources.resource_string(__name__, "data/schema.yaml"))

    try:
        jsonschema.validate(aixm, schema,
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

# Merge LoAs into airspace and return merged copy
def merge_loa(airspace, loas):
    merge_airspace = deepcopy(airspace)

    for loa in loas:
        # Add LoA airspace
        for loa_airspace in loa['airspace']:
            merge_airspace.append(loa_airspace['feature'])

            # Modify existing airspace volumes
            for mod in loa_airspace['mods']:
                vol_id = mod['volume_id']

                # Find feature
                feature = find_feature(merge_airspace, vol_id)
                if feature is None:
                    logging.error("Can't find feature %s" % str(vol_id))
                    continue

                # Append new volumes
                for vol in mod['geometry']:
                    feature['geometry'].append(vol)

                # Delete the old volume
                vol = [f for f in feature['geometry']
                       if f.get('seqno') == vol_id['seqno']]
                if vol:
                    feature['geometry'].remove(vol[0])
                else:
                    logging.warning("Can't find volume %s" % str(vol_id))

    return merge_airspace
