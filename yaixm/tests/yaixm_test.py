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

