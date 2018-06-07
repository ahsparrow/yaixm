YAIXM
=====

YAIXM is a simplified version of the FAA/EUROCONTOL Aeronautical
Information Exchange Model (AIXM) using YAML.

AIXM was chosen as the underlying model because it provides a ready made
mapping of the AIP to computer readable data. The AIP itself is (or,
possibly, will be) built on AIXM data, though unfortunately this data
isn't publicly available.

YAML is a data serialisation format specifically designed to be human
readable and writable. This is important - YAIXM data is entered manually
from the AIP.

YAIXM data can be parsed directly (YAML libraries are available for all
common computer languages) or converted to JSON before parsing.

Schema
------

YAML doesn't have a schema language. However YAIXM data can
be mapped directly to/from JSON, so [JSON Schema](http://json-schema.org/)
can be used instead. The JSON schema (written in YAML!) can be found at
yaixm/data/schema.yaml

Utilities
---------

To validate a YAIXM file against the schema:

    $ yaixm_check airspace.yaml

To convert a YAIXM file to JSON:

    $ yaixm_json airspace.yaml airspace.json

Contributing
------------

I'm Alan Sparrow

YAIXM is on [GitLab](https://gitlab.com/ahsparrow/yaixm).

Please get in touch, via GitLab or otherwise. If you've got something
to contribute it would be very welcome.
