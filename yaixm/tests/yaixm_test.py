import json
import tempfile

import yaixm

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
  input = {
    'header': {
      'airac_date': "2017-05-12",
      'author': "Bloggs",
      'email': "foo@bar.com",
      'release_timestamp': "2017-05-11T07:55:53+00:00",
      'schema_version': 1
    },
    'airspace': [
      {
        'name': "BENSON",
        'shape': [
          {
            'boundary': [
              {
                'circle': {
                  'centre': "513654N 0010545W",
                  'radius': "2 nm"
                }
              }
            ],
            'lower': "GND",
            'upper': "2203 ft"
          }
        ],
        "type": "ATZ"
      }
    ]
  }

  e = yaixm.validate(input)
  assert e is None
