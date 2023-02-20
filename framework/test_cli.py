import os
from inline_snapshot import snapshot
from cli import build

# commands:
# pytest --update-snapshots=new
# pytest --update-snapshots=failing


def get_file(path):
    with open(path) as f:
        return f.read()


def test_kitchen_sink():
    build('examples/kitchensink')

    # config
    assert get_file(
        'build/.vercel/output/config.json') == snapshot('{"version": 3, "overrides": {"build": {"contentType": "text/html"}, "regenerate": {"contentType": "text/html"}, "regenerate_without_data": {"contentType": "text/html"}, "json": {"contentType": "application/json"}, "nested/path": {"contentType": "text/html"}}}')

    # public dir
    assert get_file(
        'build/.vercel/output/static/a_public_file.txt') == snapshot(':)')

    # build page
    assert get_file(
        'build/.vercel/output/static/build') == snapshot('<h1>Hello, World!</h1>')

    # fresh page
    assert os.path.isfile(
        'build/.vercel/output/functions/fresh.func/__handler.py')
    assert os.path.isfile(
        'build/.vercel/output/functions/fresh.func/pages/fresh.py')
    assert get_file('build/.vercel/output/functions/fresh.func/.vc-config.json') == snapshot(
        '{"handler": "__handler.app", "runtime": "python3.9", "environment": {}}')
    assert get_file('build/.vercel/output/functions/fresh.func/__handler.py') == snapshot(
        'import json\nimport inspect\nimport importlib.util\n\nclass Request:\n    def __init__(self, method, path, headers, body):\n        self.method = method\n        self.path = path\n        self.headers = headers\n        self.body = body\n\n    @staticmethod\n    def from_event(event):\n        event_body = json.loads(event[\'body\'])\n        return Request(\n            event_body[\'method\'],\n            event_body[\'path\'],\n            event_body[\'headers\'],\n            event_body.get(\'body\', None)\n        )\n\ndef call_data(page, request=None):\n    # the data function is optional\n    if not (hasattr(page, \'data\') and callable(page.data)):\n        return {}\n\n    # request is an optional arg for data()\n    if len(inspect.getfullargspec(page.data).args) == 0:\n        return page.data()\n    else:\n        return page.data(request)\n\ndef call_render(page, event=None):\n    request = None\n    if event:\n        request = Request.from_event(event)\n\n    data = call_data(page, request)\n\n    # data is an optional arg for render()\n    if len(inspect.getfullargspec(page.render).args) == 0:\n        output, info = page.render()\n    else:\n        output, info = page.render(data)\n\n    ret = {\n        "statusCode": info.get(\'status_code\', 200),\n        "headers": {\'Content-Type\': \'text/html\'},\n        "body": "" if not output else output\n    }\n    ret[\'headers\'] |= info.get(\'headers\', {})\n\n    return ret\n\ndef app(event, context):\n    module_location = "pages/fresh.py"\n\n    spec = importlib.util.spec_from_file_location("", module_location)\n    page = importlib.util.module_from_spec(spec)\n    spec.loader.exec_module(page)\n\n    return call_render(page, event)\n\n')

    # regenerated page
    assert os.path.isfile(
        'build/.vercel/output/functions/regenerate.func/__handler.py')
    assert os.path.isfile(
        'build/.vercel/output/functions/regenerate.func/pages/regenerate.py')
    assert get_file('build/.vercel/output/functions/regenerate.prerender-config.json') == snapshot(
        '{"expiration": 5, "fallback": "regenerate.prerender-fallback"}')
    assert get_file('build/.vercel/output/functions/regenerate.func/__handler.py') == snapshot(
        'import json\nimport inspect\nimport importlib.util\n\nclass Request:\n    def __init__(self, method, path, headers, body):\n        self.method = method\n        self.path = path\n        self.headers = headers\n        self.body = body\n\n    @staticmethod\n    def from_event(event):\n        event_body = json.loads(event[\'body\'])\n        return Request(\n            event_body[\'method\'],\n            event_body[\'path\'],\n            event_body[\'headers\'],\n            event_body.get(\'body\', None)\n        )\n\ndef call_data(page, request=None):\n    # the data function is optional\n    if not (hasattr(page, \'data\') and callable(page.data)):\n        return {}\n\n    # request is an optional arg for data()\n    if len(inspect.getfullargspec(page.data).args) == 0:\n        return page.data()\n    else:\n        return page.data(request)\n\ndef call_render(page, event=None):\n    request = None\n    if event:\n        request = Request.from_event(event)\n\n    data = call_data(page, request)\n\n    # data is an optional arg for render()\n    if len(inspect.getfullargspec(page.render).args) == 0:\n        output, info = page.render()\n    else:\n        output, info = page.render(data)\n\n    ret = {\n        "statusCode": info.get(\'status_code\', 200),\n        "headers": {\'Content-Type\': \'text/html\'},\n        "body": "" if not output else output\n    }\n    ret[\'headers\'] |= info.get(\'headers\', {})\n\n    return ret\n\ndef app(event, context):\n    module_location = "pages/regenerate.py"\n\n    spec = importlib.util.spec_from_file_location("", module_location)\n    page = importlib.util.module_from_spec(spec)\n    spec.loader.exec_module(page)\n\n    return call_render(page, event)\n\n')

    # nested path
    assert get_file(
        'build/.vercel/output/static/nested/path') == snapshot("<h1>I'm a nested path</h1>")
