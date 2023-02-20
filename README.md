# Jar 🫙

Jar is a toy Python framework, implemented in about 200 lines of code (see cli.py).

I built it to explore some ideas around framework APIs. Please don't actually use it.

It deploys to Vercel via the [Build Output API](https://vercel.com/docs/build-output-api/v3). 

It's called Jar because it has almost no features and you need to fill it up yourself!

## Docs

https://jar-docs.vercel.app

## Features

Jar uses a file-system router.

Pages are Python files that render content. They're put in the `pages` directory.

Public files (like CSS and other media files) go in the `public` directory and are served from the root path.

- Build pages aka [Static Files](https://vercel.com/docs/build-output-api/v3#vercel-primitives/static-files)
- Fresh pages aka [Serverless Functions](https://vercel.com/docs/build-output-api/v3#vercel-primitives/serverless-functions)
- Regenerated pages aka [Prerender Functions](https://vercel.com/docs/build-output-api/v3#vercel-primitives/prerender-functions)

Checkout the source for the kitchen sink example, or this docs website.

A typical project is structured like this:

```text
project/
├─ public/
│  ├─ favicon.ico
├─ pages/
│  ├─ index.py
```

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

## Tests

- `pip3 install -r framework/requirements.txt`
- `pytest`

## Deploy Docs

- `pip3 install -r framework/requirements.txt`
- `cd examples/docs && pip3 install -r requirements.txt --target . && cd ../..`
- `python3 framework/cli.py build examples/docs`
- `cd build && vercel --prebuilt --prod && cd ..`

## Deploy Kitchen Sink

- `pip3 install -r framework/requirements.txt`
- `python3 framework/cli.py build examples/kitchensink`
- `cd build && vercel --prebuilt`
