import argparse
import sys

import yaml

import yaixm

def check():
  parser = argparse.ArgumentParser()
  parser.add_argument("airspace_file", nargs="?",
                      help="YAML airspace file",
                      type=argparse.FileType("r"), default=sys.stdin)
  args = parser.parse_args()

  # Load airspace
  airspace = yaml.load(args.airspace_file)

  # Validate and write any errors to stderr
  e = yaixm.validate(airspace)
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
  airspace = yaml.load(args.airspace_file)

  # Convert to openair
  oa = yaixm.openair(airspace)

  # Add DOS line endings
  oa.append("")
  output_oa = "\r\n".join(oa)

  # Don't accept anything other than ASCII
  output_oa = output_oa.encode("ascii").decode("ascii")

  args.openair_file.write(output_oa)
