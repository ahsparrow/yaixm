from copy import deepcopy
import json
import tempfile

import yaml

import yaixm

TEST_AIRSPACE = {
    'release': {
        'airac_date': "2017-05-12T00:00:00Z",
        'timestamp': "2017-05-11T07:55:53+00:00",
        'schema_version': 1,
        'commit': "unknown"
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
        'type': "ATZ",
        'rules': ["NOTAM"]
    }, {
        'name': "FOOBAR",
        'id': "foobar",
        'geometry': [{
            'boundary': [{'circle': {'centre': "513654N 0010545W",
                                     'radius': "2 nm"}}],
            'lower': "SFC",
            'upper': "2203 ft"
        }],
        'type': "CTA"
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
    }],
    'rat': [{
        'name': "RAT TEST",
        'geometry': [{
            'boundary': [{'circle': {'centre': "513654N 0010545W",
                                     'radius': "2 nm"}}],
            'lower': "SFC",
            'upper': "2203 ft"
        }],
        "type": "OTHER",
        "localtype": "RAT"
    }],
    'obstacle': [{
        'id': "UK1234A567B",
        'elevation': "500 ft",
        'position': "512345N 0012345W",
        'type': "OBST"
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
    assert len(oa.split("\n")) == 14

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

def test_latlon():
    lat, lon = yaixm.parse_latlon("521234N 1234455E")
    assert abs(lat - (52 + 12 / 60 + 34 / 3600)) < 1E-6
    assert abs(lon - (123 + 44 / 60 + 55 / 3600)) < 1E-6

def test_latlon_dec():
    lat, lon = yaixm.parse_latlon("521234.12N 1234455.345E")
    assert abs(lat - (52 + 12 / 60 + 34.12 / 3600)) < 1E-6
    assert abs(lon - (123 + 44 / 60 + 55.345 / 3600)) < 1E-6

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
    assert len(oa.split("\n")) == 14

    # Filter by name
    f = yaixm.make_filter(exclude=[{'name': "BENSON", 'type': "ATZ"}])
    converter = yaixm.Openair(filter_func=f)
    oa = converter.convert(input['airspace'])
    assert len(oa.split("\n")) == 7

    # Filter by latitude
    f = yaixm.make_filter(north=50)
    converter = yaixm.Openair(filter_func=f)
    oa = converter.convert(input['airspace'])
    assert oa == ""

def test_openair_obstacle():
    converter = yaixm.Openair()
    oa = converter.convert([], TEST_AIRSPACE['obstacle'])
    assert len(oa.split("\n")) == 7

def test_tnp():
    converter = yaixm.Tnp()
    oa = converter.convert([], TEST_AIRSPACE['obstacle'])
    assert len(oa.split("\n")) == 9

def test_merge_loa():
    input = dict(TEST_AIRSPACE)
    airspace = yaixm.merge_loa(TEST_AIRSPACE['airspace'], TEST_AIRSPACE['loa'])

    names = [feature['name'] for feature in airspace]
    assert "TEST BOX" in names

def test_merge_service():
    service = {'foobar': 123.4}

    airspace = yaixm.merge_service(TEST_AIRSPACE['airspace'], service)
    assert 'frequency' in airspace[1]

def test_header():
    input = dict(TEST_AIRSPACE)

    converter = yaixm.Openair(header="Header line 1\nHeader line 2")
    oa = converter.convert(input['airspace'])

    assert oa.splitlines()[0] == "* Header line 1"
    assert oa.splitlines()[1] == "* Header line 2"

def test_notam():
    input = dict(TEST_AIRSPACE)

    converter = yaixm.Openair()
    oa = converter.convert(input['airspace'])

    assert "AN BENSON ATZ (NOTAM)" in oa

def test_openair_freq():
    service = {'foobar': 123.4}
    airspace = yaixm.merge_service(TEST_AIRSPACE['airspace'], service)

    converter = yaixm.Openair()
    oa = converter.convert(airspace)

    assert "AN FOOBAR 123.400" in oa
