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

    "feature", "add", "delete",

    "id", "seqno", "upper", "lower", "class", "rules", "boundary",

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

    for loa in loas:
        # LoA consists of one or more new airspace features
        for loa_airspace in loa['airspace']:
            # Add new LoA airspace feature
            merge_airspace.append(loa_airspace['feature'])

            # Each new feature modifies zero or more existing volumes
            for mod in loa_airspace['mods']:
                vol_id = mod['volume_id']

                # Find feature containing volume to be replaced
                feature = find_feature(merge_airspace, vol_id)
                if feature is None:
                    logging.error("Can't find feature %s" % str(vol_id))
                    continue

                # Delete the old volume
                if 'seqno' not in vol_id:
                    # If seqno not specified only delete if single volume
                    if len(feature['geometry']) == 1:
                        feature['geometry'] = []
                    else:
                        logging.error("Seqno required for %s" % str(vol_id))
                else:
                    # Search and destroy volume
                    vol = [f for f in feature['geometry']
                           if f.get('seqno') == vol_id['seqno']]
                    if vol:
                        feature['geometry'].remove(vol[0])
                    else:
                        logging.warning("Can't find volume %s" % str(vol_id))

                # Append (zero or more) new volumes
                for vol in mod['geometry']:
                    feature['geometry'].append(vol)

    return merge_airspace
