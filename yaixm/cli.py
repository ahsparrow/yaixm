import argparse
import json
import sys

import yaml

from .helpers import load, validate
from .openair import convert as openair

def check():
  parser = argparse.ArgumentParser()
  parser.add_argument("airspace_file", nargs="?",
                      help="YAML airspace file",
                      type=argparse.FileType("r"), default=sys.stdin)
  args = parser.parse_args()

  # Validate and write any errors to stderr
  e = validate(args.airspace)
  if e:
    print(e, file=sys.stderr)
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
  oa = openair(airspace)

  # Add DOS line endings
  oa.append("")
  output_oa = "\r\n".join(oa)

  # Don't accept anything other than ASCII
  output_oa = output_oa.encode("ascii").decode("ascii")

  args.openair_file.write(output_oa)

def yaml_to_json():
  import argparse

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

