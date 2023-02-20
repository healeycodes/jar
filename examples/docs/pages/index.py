import marko


def render():
    text = """
# Jar 🫙

Jar is a toy Python framework, implemented in about 200 lines of code (see [cli.py](https://github.com/healeycodes/jar/blob/main/framework/cli.py)). It's [open source](https://github.com/healeycodes/jar).

I built it to explore some ideas around framework APIs. Please don't actually use it.

It deploys to Vercel via the [Build Output API](https://vercel.com/docs/build-output-api/v3). 

This website runs on Jar!

## Features

Jar uses a file-system router.

Pages are Python files that render content. They're put in the `pages` directory.

Public files (like CSS and other media files) go in the `public` directory and are served from the root path.

- Build pages aka [Static Files](https://vercel.com/docs/build-output-api/v3#vercel-primitives/static-files)
- Fresh pages aka [Serverless Functions](https://vercel.com/docs/build-output-api/v3#vercel-primitives/serverless-functions)
- Regenerated pages aka [Prerender Functions](https://vercel.com/docs/build-output-api/v3#vercel-primitives/prerender-functions)

Checkout the source for the [kitchen sink example](https://github.com/healeycodes/jar/tree/main/examples/kitchensink), or [this docs website](https://github.com/healeycodes/jar/tree/main/examples/docs).

### Build pages

Generated once at build time. Served as a static file.

```python
import time

def render(data):
    return f"<h1>{data['text']} I was built at {data['time']}</h1>", {}

def data():
    return {
        "text": "Hello, World!",
        "time": time.time(),
    }
```

### Fresh pages

Generated for each request. Similar to Server-Side Rendering (SSR).

```python
import json
import time


def render(data):
    content = f"<h1>Fresh Page rendered at {data['time']}</h1>"
    content += f"<code>{data['request']}</code>"
    return content, {}


def data(request):
    return {
        "time": time.time(),
        "request": json.dumps({
            "method": request.method,
            "path": request.path,
            "headers": request.headers,
            "body": request.body
        }, indent=4)
    }


def config():
    return {
        "fresh": {}
    }
```

### Regenerated Pages

Similar to Next.js's [Incremental Static Regeneration](https://nextjs.org/docs/basic-features/data-fetching/incremental-static-regeneration).

```python
import time


def render(data):
    return f"<h1>Regenerated Page, last rendered at {data['time']}</h1>", {}

def data(request=None):
    return {
        "time": time.time(),
    }

def config():
    return {
        "regenerate": {
            "every": 5
        }
    }
```

<br>
"""
    return f"""
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="water.css">
    <link href="https://unpkg.com/prismjs@1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
</head>
<body>
    {marko.convert(text)}
    <script src="https://unpkg.com/prismjs@1.29.0/components/prism-core.min.js"></script>
    <script src="https://unpkg.com/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
</body>
</html>
""", {}
