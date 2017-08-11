import json
import tempfile

import yaixm

TEST_AIRSPACE = {
    'release': {
        'airac_date': "2017-05-12",
        'release_timestamp': "2017-05-11T07:55:53+00:00",
        'schema_version': 1
    },
    'airspace': [{
        'name': "BENSON",
        'geometry': [{
            'id': '$benson',
            'boundary': [{
                'circle': {
                    'centre': "513654N 0010545W",
                    'radius': "2 nm"
                 }
            }],
            'lower': "GND",
            'upper': "2203 ft"
        }],
        "type": "ATZ"
    }],
    "loa": [{
        "name": "LOA FOO",
        "airspace": [{
            "add": [{
                "name": "TEST BOX",
                "type": "CTR",
                "geometry": [{
                    "lower": "GND",
                    "upper": "1000 ft",
                    "boundary" : [{
                        'circle': {
                            'centre': "513654N 0010545W",
                            'radius': "2 nm"
                        }
                    }]
                }]
            },
            {
                "name": "FOONAR",
                "type": "ATZ",
                "geometry": [{
                    "lower": "FL100",
                    "upper": "FL200",
                    "boundary" : [{
                        'circle': {
                            'centre': "513654N 0010545W",
                            'radius': "2 nm"
                        }
                    }]
                }]
            }],
            "delete": ["$foo", "$bar"]
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
    input = dict(TEST_AIRSPACE)
    input['airspace'][0]['type'] = "NOT REALLY A TYPE"
    e = yaixm.validate(input)
    assert e

def test_openair():
    input = dict(TEST_AIRSPACE)
    oa = yaixm.openair(input['airspace'])
    assert len(oa) == 6

def test_openair_name():
    def name_func(feature, volume):
        return "FOONAME"

    input = dict(TEST_AIRSPACE)
    oa = yaixm.openair(input['airspace'], nfunc=name_func)

    assert oa[1] == "AN FOONAME"

def test_openair_class():
    def class_func(feature, volume):
        return "A"

    input = dict(TEST_AIRSPACE)
    oa = yaixm.openair(input['airspace'], cfunc=class_func)

    assert oa[0] == "AC A"
