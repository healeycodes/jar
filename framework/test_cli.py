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


def test_docs():
    build('examples/docs')

    assert get_file(
        'build/.vercel/output/static/index') == snapshot('\n<html>\n<head>\n    <meta charset="UTF-8">\n    <link rel="stylesheet" href="water.css">\n    <link href="https://unpkg.com/prismjs@1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">\n</head>\n<body>\n    <h1>Jar \U0001fad9</h1>\n<p>Jar is a toy Python framework, implemented in about 200 lines of code. It\'s open source.</p>\n<p>I built it to explore some ideas around framework APIs. Please don\'t actually use it.</p>\n<p>It deploys to Vercel via the <a href="https://vercel.com/docs/build-output-api/v3">Build Output API</a>. </p>\n<p>This website runs on Jar!</p>\n<h2>Features</h2>\n<p>Jar uses a file-system router.</p>\n<p>Pages are Python files that render content. They\'re put in the <code>pages</code> directory.</p>\n<p>Public files (like CSS and other media files) go in the <code>public</code> directory and are served from the root path.</p>\n<ul>\n<li>Build pages aka <a href="https://vercel.com/docs/build-output-api/v3#vercel-primitives/static-files">Static Files</a></li>\n<li>Fresh pages aka <a href="https://vercel.com/docs/build-output-api/v3#vercel-primitives/serverless-functions">Serverless Functions</a></li>\n<li>Regenerated pages aka <a href="https://vercel.com/docs/build-output-api/v3#vercel-primitives/prerender-functions">Prerender Functions</a></li>\n</ul>\n<p>Checkout the source for the kitchen sink example, or this docs website.</p>\n<h3>Build pages</h3>\n<p>Generated once at build time. Served as a static file.</p>\n<pre><code class="language-python">import time\n\ndef render(data):\n    return f&quot;&lt;h1&gt;{data[&#x27;text&#x27;]} I was built at {data[&#x27;time&#x27;]}&lt;/h1&gt;&quot;, {}\n\ndef data():\n    return {\n        &quot;text&quot;: &quot;Hello, World!&quot;,\n        &quot;time&quot;: time.time(),\n    }\n</code></pre>\n<h3>Fresh pages</h3>\n<p>Generated for each request. Similar to Server-Side Rendering (SSR).</p>\n<pre><code class="language-python">import json\nimport time\n\n\ndef render(data):\n    content = f&quot;&lt;h1&gt;Fresh Page rendered at {data[&#x27;time&#x27;]}&lt;/h1&gt;&quot;\n    content += f&quot;&lt;code&gt;{data[&#x27;request&#x27;]}&lt;/code&gt;&quot;\n    return content, {}\n\n\ndef data(request):\n    return {\n        &quot;time&quot;: time.time(),\n        &quot;request&quot;: json.dumps({\n            &quot;method&quot;: request.method,\n            &quot;path&quot;: request.path,\n            &quot;headers&quot;: request.headers,\n            &quot;body&quot;: request.body\n        }, indent=4)\n    }\n\n\ndef config():\n    return {\n        &quot;fresh&quot;: {}\n    }\n</code></pre>\n<h3>Regenerated Pages</h3>\n<p>Similar to Next.js\'s <a href="https://nextjs.org/docs/basic-features/data-fetching/incremental-static-regeneration">Incremental Static Regeneration</a>.</p>\n<pre><code class="language-python">import time\n\n\ndef render(data):\n    return f&quot;&lt;h1&gt;Regenerated Page, last rendered at {data[&#x27;time&#x27;]}&lt;/h1&gt;&quot;, {}\n\ndef data(request=None):\n    return {\n        &quot;time&quot;: time.time(),\n    }\n\ndef config():\n    return {\n        &quot;regenerate&quot;: {\n            &quot;every&quot;: 5\n        }\n    }\n</code></pre>\n<br>\n\n    <script src="https://unpkg.com/prismjs@1.29.0/components/prism-core.min.js"></script>\n    <script src="https://unpkg.com/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>\n</body>\n</html>\n')
