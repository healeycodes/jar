import json


def render():
    return json.dumps({"foo": "bar"}), {'headers': {'Content-Type': 'application/json'}}
