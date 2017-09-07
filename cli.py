import sys

import yaixm.cli

script_name = sys.argv[1]
sys.argv.pop(1)

if script_name == "openair":
    yaixm.cli.openair()
elif script_name == "tnp":
    yaixm.cli.tnp()
elif script_name == "check":
    yaixm.cli.check()
elif script_name == "json":
    yaixm.cli.to_json()
else:
    print("Unrecognised script: " + script_name, file=sys.stderr)

