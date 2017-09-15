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

import math

from .helpers import dms, minmax_lat

# Filter factory
def make_filter(noatz=True, microlight=True, hgl=True,
                gliding_site=True, north=59, south=49, exclude=None):
    def airfilter(volume, feature):
        as_type = feature['type']
        as_name = feature['name']

        # Exclude by name/type
        if exclude:
            for e in exclude:
                if as_name == e['name'] and as_type == e['type']:
                    return False

        # Non-ATZ airfields
        if not noatz and feature.get('localtype') == "NOATZ":
            return False

        # Microlight strips
        if not microlight and feature.get('localtype') == "UL":
            return False

        # HIRTA, GVS and LASER
        if not hgl and feature.get('localtype') in ["HIRTA", "GVS", "LASER"]:
            return false

        # Gliding sites
        if (not gliding_site and feature['type'] == "OTHER" and
            feature.get('localtype') == "GLIDER"):
            return False

        min_lat, max_lat = minmax_lat(volume)
        if (min_lat > math.radians(north)) or (max_lat < math.radians(south)):
            return False

        return True

    return airfilter

# Default filter includes everything
default_filter = make_filter()

# Default name
def default_name(volume, feature):
    rules = feature.get('rules', []) + volume.get('rules', [])

    if 'name' in volume:
        return volume['name']

    else:
        if 'localtype' in feature:
            localtype = feature['localtype']
            if localtype == "GLIDER":
                subs = ""
            elif localtype == "NOATZ":
                subs = "A/F"
            else:
                subs = localtype

        elif "RAZ" in rules:
            subs = "RAZ"

        elif "RMZ" in rules:
            subs = "RMZ"

        elif "TMZ" in rules:
            subs = "TMZ"

        elif feature['type'] in ["ATZ", "CTA", "CTR", "TMA"]:
            subs = feature['type']

        else:
            subs = ""

        if subs:
            return "%s %s" % (feature['name'], subs)
        else:
            return feature['name']

# Default Openair type
def default_openair_type(volume, feature):
    as_type = feature['type']
    local_type = feature.get('localtype')
    rules = feature.get('rules', []) + volume.get('rules', [])

    if as_type == "D" or local_type == "DZ":
        out_type = "Q"
    elif as_type == "R":
        out_type = "R"
    elif as_type == "P":
        out_type = "P"
    elif as_type == "ATZ" or local_type == "ILS":
        out_type = "CTR"
    elif local_type == "MATZ":
        out_type = "MATZ"
    elif local_type == "TMZ" or "TMZ" in rules:
        out_type = "TMZ"
    elif local_type == "RMZ" or "RMZ" in rules:
        out_type = "RMZ"
    elif local_type in ["GLIDER", "NOATZ", "UL"]:
        out_type = "G"
    else:
        out_type = volume.get('class') or feature.get('class') or "OTHER"

    return out_type

# Default TNP class
def default_tnp_class(volume, feature):
    local_type = feature.get('localtype')

    if volume.get('class'):
        return volume['class']
    elif feature.get('class'):
        return feature['class']
    else:
        return None

# Default TNP type
def default_tnp_type(volume, feature):
    as_type = feature['type']
    local_type = feature.get('localtype')
    rules = feature.get('rules', []) + volume.get('rules', [])

    if as_type == "D" or local_type == "DZ":
        out_type = "DANGER"
    elif as_type == "P":
        out_type = "PROHIBITED"
    elif as_type == "R":
        out_type = "RESTRICTED"
    elif as_type in ["ATZ", "CTA", "CTR", "TMA"] or local_type == "ILS":
        out_type = "CTA/CTR"
    elif local_type == "MATZ":
        out_type = "MATZ"
    elif local_type == "TMZ" or "TMZ" in rules:
        out_type = "TMZ"
    elif local_type == "RMZ" or "RMZ" in rules:
        out_type = "RMZ"
    elif as_type == "AWY":
        out_type = "AIRWAYS"
    else:
        out_type = "OTHER"

    return out_type

# Base class for TNP and OpenAir converters
class Converter():
    def format_latlon(self, latlon):
        return self.__class__.latlon_fmt.format(*[dms(x)
                                                  for x in latlon.split()])

    def do_line(self, line):
        output = []
        for point in line:
            output.extend(self.do_point(point))

        return output

    def do_boundary(self, boundary):
        output = []
        for segment in boundary:
            segtype = list(segment.keys())[0]
            if segtype == 'circle':
                output.extend(self.do_circle(segment['circle']))
            elif segtype == 'line':
                output.extend(self.do_line(segment['line']))
                point = segment['line'][-1]
            elif segtype == 'arc':
                output.extend(self.do_arc(segment['arc'], point))
                point = segment['arc']['to']

        # Close the polygon
        if 'line' in boundary[0]:
            if 'line' in boundary[-1]:
                output.extend(self.do_point(boundary[0]['line'][0]))
            elif 'arc' in boundary[-1]:
              if boundary[0]['line'][0] != boundary[-1]['arc']['to']:
                  output.extend(self.do_point(boundary[0]['line'][0]))

        return output

    def start(self):
        return []

    def end(self):
        return []

    def convert(self, airspace):
        output = self.start()
        for feature in airspace:
            for volume in feature['geometry']:
                if self.filter_func(volume, feature):
                    x = self.do_volume(volume, feature)
                    output.extend(x)

        output.extend(self.end())

        return "\n".join(output)

# Openair converter
class Openair(Converter):
    latlon_fmt =  "{0[d]:02d}:{0[m]:02d}:{0[s]:02d} {0[h]} "\
                  "{1[d]:03d}:{1[m]:02d}:{1[s]:02d} {1[h]}"

    def __init__(self, filter_func=default_filter, name_func=default_name,
                 type_func=default_openair_type):
        self.filter_func = filter_func
        self.name_func = name_func
        self.type_func = type_func

    def do_name(self, name):
        return ["AN %s" % name]

    def do_type(self, as_type):
        return ["AC %s" % as_type]

    # Upper and lower levels
    def do_levels(self, volume):
        def level_str(level):
          if level == "GND":
              return "SFC"
          elif level.endswith('ft'):
              return level[:-3] + "ALT"
          else:
              return level

        return ["AL %s" % level_str(volume['lower']),
                "AH %s" % level_str(volume['upper'])]

    # Centre of arc or circle
    def centre(self, latlon):
        return "V X=%s" % self.format_latlon(latlon)

    # Airspace circle boundary
    def do_circle(self, circle):
        return [self.centre(circle['centre']),
                "DC %s" % circle['radius'].split()[0]]

    # Airspace boundary point
    def do_point(self, point):
        return ["DP %s" % self.format_latlon(point)]

    # Airspace arc direction
    def dir(self, dir):
        if dir == "cw":
            return "V D=+"
        else:
            return "V D=-"

    # Airspace arc from/to points
    def fromto(self, from_point, to_point):
        return "DB %s, %s" % (self.format_latlon(from_point),
                              self.format_latlon(to_point))

    # Airspace arc
    def do_arc(self, arc, from_point):
        return [self.dir(arc['dir']),
                self.centre(arc['centre']),
                self.fromto(from_point, arc['to'])]

    def do_volume(self, volume, feature):
        return (["*"] +
                self.do_type(self.type_func(volume, feature)) +
                self.do_name(self.name_func(volume,feature)) +
                self.do_levels(volume) +
                self.do_boundary(volume['boundary']))

# TNP converter
# IMPORTANT - this implement starts each airspace block with TITLE,
# followed by CLASS and TYPE. This isn't compatible with all  programs,
# for example XCSoar
class Tnp(Converter):
    latlon_fmt = "{0[h]}{0[d]:02d}{0[m]:02d}{0[s]:02d} "\
                 "{1[h]}{1[d]:03d}{1[m]:02d}{1[s]:02d}"

    def __init__(self, filter_func=default_filter, name_func=default_name,
                 class_func=default_tnp_class, type_func=default_tnp_type):
        self.filter_func = filter_func
        self.name_func = name_func
        self.class_func = class_func
        self.type_func = type_func

    def end(self):
        return ['#', 'END']

    def do_name(self, name):
        return ["TITLE=%s" % name]

    def do_class(self, as_class):
        return ["CLASS=%s" % (as_class or "")]

    def do_type(self, as_type):
        return ["TYPE=%s" % as_type]

    def do_levels(self, volume):
        def level_str(level):
          if level == "GND":
              return "SFC"
          elif level.endswith('ft'):
              return level[:-3] + "ALT"
          else:
              return level

        return ["BASE=%s" % level_str(volume['lower']),
                "TOPS=%s" % level_str(volume['upper'])]

    def do_point(self, point):
        return ["POINT=%s" % self.format_latlon(point)]

    def do_circle(self, circle):
        radius = circle['radius'].split()[0]
        centre = self.format_latlon(circle['centre'])
        return ["CIRCLE RADIUS=%s CENTRE=%s" % (radius, centre)]

    def do_arc(self, arc, from_point):
        dir = "CLOCKWISE" if arc['dir'] == 'cw' else "ANTI-CLOCKWISE"
        radius = arc['radius'].split()[0]
        centre = self.format_latlon(arc['centre'])
        to = self.format_latlon(arc['to'])
        return ["%s RADIUS=%s CENTRE=%s TO=%s" % (dir, radius, centre, to)]

    def do_volume(self, volume, feature):
        tnp = ["#"] +\
              self.do_name(self.name_func(volume,feature)) +\
              self.do_type(self.type_func(volume, feature)) +\
              self.do_class(self.class_func(volume, feature)) +\
              self.do_levels(volume) +\
              self.do_boundary(volume['boundary'])

        # If class is defined then order is type/class, otherwise class/type.
        # So XCSoar type is airspace class if defined or airspace type if not.
        if tnp[3] == "CLASS=":
            tnp[2], tnp[3] = tnp[3], tnp[2]

        return tnp
