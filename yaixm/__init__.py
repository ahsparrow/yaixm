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
# along with Airplot.  If not, see <http://www.gnu.org/licenses/>.

import jsonschema
import pkg_resources
import yaml
try:
  from yaml import CLoader as Loader
except ImportError:
  from yaml import Loader

from yaixm.openair import convert as openair

def load(stream, json=False):
  if json:
    if hasattr(stream, 'read')
      data = json.load(stream)
    else:
      data = json.loads(stream)
  else:
    data = yaml.load(stream, Loader=Loader)

  return data

def dump(airspace, json=False):
  with

def validate(airspace):
  schema = load(pkg_resources.resource_string(__name__, "data/schema.yaml"))

  try:
    jsonschema.validate(airspace, schema,
                        format_checker=jsonschema.FormatChecker())
  except jsonschema.exceptions.ValidationError as e:
    return e

  return None
