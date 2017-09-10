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

import argparse
import json
import sys

from .convert import Openair, Tnp
from .helpers import load, validate
from .helpers import oasort as oa_sort

def check():
    parser = argparse.ArgumentParser()
    parser.add_argument("airspace_file", nargs="?",
                        help="YAML airspace file",
                        type=argparse.FileType("r"), default=sys.stdin)
    args = parser.parse_args()

    # Load airspace
    airspace = load(args.airspace_file)

    # Validate and write any errors to stderr
    e = validate(airspace)
    if e:
        print(e.message, file=sys.stderr)
        sys.exit(1)

def openair():
    parser = argparse.ArgumentParser()
    parser.add_argument("airspace_file", nargs="?",
                        help="YAML airspace file",
                        type=argparse.FileType("r"), default=sys.stdin)
    parser.add_argument("openair_file", nargs="?",
                        help="Openair output file, stdout if not specified",
                        type=argparse.FileType("w", encoding="ascii"),
                        default=sys.stdout)
    args = parser.parse_args()

    # Load airspace
    airspace = load(args.airspace_file)

    # Convert to openair
    convert = Openair()
    oa = convert.convert(airspace['airspace'])

    # Don't accept anything other than ASCII
    output_oa = oa.encode("ascii").decode("ascii")

    args.openair_file.write(output_oa)

def tnp():
    parser = argparse.ArgumentParser()
    parser.add_argument("airspace_file", nargs="?",
                        help="YAML airspace file",
                        type=argparse.FileType("r"), default=sys.stdin)
    parser.add_argument("tnp_file", nargs="?",
                        help="TNP output file, stdout if not specified",
                        type=argparse.FileType("w", encoding="ascii"),
                        default=sys.stdout)
    args = parser.parse_args()

    # Load airspace
    airspace = load(args.airspace_file)

    # Convert to openair
    convert = Tnp()
    oa = convert.convert(airspace['airspace'])

    # Don't accept anything other than ASCII
    output_oa = oa.encode("ascii").decode("ascii")

    args.tnp_file.write(output_oa)

def to_json():
    parser = argparse.ArgumentParser()
    parser.add_argument("yaml_file", nargs="?",
                        help="YAML input file, stdin if not specified",
                        type=argparse.FileType("r"), default=sys.stdin)
    parser.add_argument("json_file", nargs="?",
                        help="JSON output file, stdout if not specified",
                        type=argparse.FileType("w"), default=sys.stdout)
    parser.add_argument("-i", "--indent", type=int, help="indent level",
                        default=None)
    parser.add_argument("-s", "--sort", help="sort keys", action="store_true")
    args = parser.parse_args()

    data = load(args.yaml_file)
    json.dump(data, args.json_file, sort_keys=args.sort, indent=args.indent)

    if args.json_file is sys.stdout:
        print()

def oasort():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", nargs="?",
                        help="Input Openair file, stdin if not specified",
                        type=argparse.FileType("r"), default=sys.stdin)
    parser.add_argument("output_file", nargs="?",
                        help="Sorted (and stripped) Openair file, stdout if not specified",
                        type=argparse.FileType("w", encoding="ascii"),
                        default=sys.stdout)
    args = parser.parse_args()

    # Sort input file
    openair = oa_sort(args.input_file)

    for oa in openair:
        args.output_file.write(oa)
