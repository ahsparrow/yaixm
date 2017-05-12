import argparse
import sys

import yaml

import yaixm

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("airspace_file", nargs="?",
                      help="YAML airspace file",
                      type=argparse.FileType("r"), default=sys.stdin)
  args = parser.parse_args()

  # Load airspace
  airspace = yaml.load(args.airspace_file)

  e = yaixm.validate(airspace)
  if e:
    print(e, file=sys.stderr)
    sys.exit(1)
