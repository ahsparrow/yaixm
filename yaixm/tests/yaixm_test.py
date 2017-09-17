from copy import deepcopy
import json
import math
import tempfile

import yaml

import yaixm

TEST_AIRSPACE = {
    'release': {
        'airac_date': "2017-05-12T00:00:00Z",
        'timestamp': "2017-05-11T07:55:53+00:00",
        'schema_version': 1
    },
    'airspace': [{
        'name': "BENSON",
        'geometry': [{
            'id': 'benson',
            'boundary': [{'circle': {'centre': "513654N 0010545W",
                                     'radius': "2 nm"}}],
            'lower': "SFC",
            'upper': "2203 ft"
        }],
        "type": "ATZ"
    }],
    "loa": [{
        "name": "LOA FOO",
        "areas": [{
            "name": "FOO-1",
            "add": [{
                "name": "TEST BOX",
                "type": "CTR",
                "geometry": [{
                    "lower": "SFC",
                    "upper": "1000 ft",
                    "boundary" : [{'line': ["513654N 0010545W",
                                            "513654N 0010545W"]}]
                }]
            }],
            "replace": [{
                "id": "foobar",
                "geometry": []
            }, {
                "id": "barfoo",
                "geometry": [{
                    "name": "SPECIAL-NAME",
                    "lower": "SFC",
                    "upper": "1000 ft",
                    "boundary" : [{
                        'circle': {
                            'centre': "513654N 0010545W",
                            'radius': "2 nm"
                        }
                    }]
                }]
            }],
        }]
    }]
}

def create_tmp_text_file(data):
    f = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
    f.write(data)
    f.seek(0)

    return f

def create_tmp_binary_file(data):
    f = tempfile.TemporaryFile(mode="w+b")
    f.write(data)
    f.seek(0)

    return f

def test_text_read():
    input = {"test": "¡Hola!"}
    with create_tmp_text_file(json.dumps(input)) as f:
        output = yaixm.load(f)

    assert input == output

def test_binary_read():
    input = {"test": "¡Hola!"}
    with create_tmp_binary_file(bytes(json.dumps(input), encoding="utf-8")) as f:
        output = yaixm.load(f)

        assert input == output

def test_sting_read():
    input = {"test": "¡Hola!"}
    output = yaixm.load(json.dumps(input))

    assert input == output

def test_json_text_read():
    input = {'test': "¡Hola!"}
    with create_tmp_text_file(json.dumps(input)) as f:
        output = yaixm.load(f, json=True)

    assert input == output

def test_json_sting_read():
    input = {"test": "¡Hola!"}
    output = yaixm.load(json.dumps(input), json=True)

    assert input == output

def test_validation_good():
    input = dict(TEST_AIRSPACE)
    e = yaixm.validate(input)
    assert e is None

def test_validation_bad():
    input = dict(deepcopy(TEST_AIRSPACE))
    input['airspace'][0]['type'] = "NOT REALLY A TYPE"
    e = yaixm.validate(input)
    assert e

def test_openair():
    input = dict(TEST_AIRSPACE)
    converter = yaixm.Openair()
    oa = converter.convert(input['airspace'])
    assert len(oa.split("\n")) == 7

def test_openair_name():
    def name_func(feature, volume):
        return "FOONAME"

    input = dict(TEST_AIRSPACE)
    converter = yaixm.Openair(name_func=name_func)
    oa = converter.convert(input['airspace'])
    oa = oa.split("\n")

    assert oa[2] == "AN FOONAME"

def test_openair_class():
    def type_func(feature, volume):
        return "A"

    input = dict(TEST_AIRSPACE)
    converter = yaixm.Openair(type_func=type_func)
    oa = converter.convert(input['airspace'])
    oa = oa.split("\n")

    assert oa[1] == "AC A"

def test_representer():
    input = dict(TEST_AIRSPACE)
    yaml.add_representer(dict, yaixm.ordered_map_representer)
    yaml.dump(input)

def test_radians():
    x = yaixm.radians("521234N")
    assert abs(x - math.radians(52 + 12/60 + 34/3600)) < 1E-6

    x = yaixm.radians("0025432W")
    assert abs(x + math.radians(2 + 54/60 + 32/3600)) < 1E-6

def test_timestamp():
    input = "2017-09-13T09:00:00Z"
    output  = yaixm.load("2017-09-13T09:00:00Z")
    assert input == output

def test_make_filter():
    input = dict(TEST_AIRSPACE)

    # Default filter
    f = yaixm.make_filter()
    converter = yaixm.Openair(filter_func=f)
    oa = converter.convert(input['airspace'])
    assert len(oa.split("\n")) == 7

    # Filter by name
    f = yaixm.make_filter(exclude=[{'name': "BENSON", 'type': "ATZ"}])
    converter = yaixm.Openair(filter_func=f)
    oa = converter.convert(input['airspace'])
    assert oa == ""

    # Filter by latitude
    f = yaixm.make_filter(north=50)
    converter = yaixm.Openair(filter_func=f)
    oa = converter.convert(input['airspace'])
    assert oa == ""
