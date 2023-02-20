[![CI](https://github.com/healeycodes/jar/actions/workflows/ci.yml/badge.svg)](https://github.com/healeycodes/jar/actions/workflows/ci.yml)

# Jar 🫙

Jar is a toy Python web framework, implemented in about 200 lines of code (see [cli.py](https://github.com/healeycodes/jar/blob/main/framework/cli.py)).

I built it to explore some ideas around framework APIs. Please don't actually use it.

It deploys to Vercel via the [Build Output API](https://vercel.com/docs/build-output-api/v3). 

It's called Jar because it has almost no features and you need to fill it up yourself!

## Docs

https://jar-docs.vercel.app

## Features

Jar uses file-system routing.

Pages are Python files that render content. They're put in the `pages` directory.

- Build pages aka [Static Files](https://vercel.com/docs/build-output-api/v3#vercel-primitives/static-files)
- Fresh pages aka [Serverless Functions](https://vercel.com/docs/build-output-api/v3#vercel-primitives/serverless-functions)
- Regenerated pages aka [Prerender Functions](https://vercel.com/docs/build-output-api/v3#vercel-primitives/prerender-functions)

Public files (like CSS and other media files) go in the `public` directory and are served from the root path.

Checkout the source for the [kitchen sink example](https://github.com/healeycodes/jar/tree/main/examples/kitchensink), or [the docs website](https://github.com/healeycodes/jar/tree/main/examples/docs).

A typical project is structured like this:

```text
project/
├─ pages/
│  ├─ index.py
├─ public/
│  ├─ favicon.ico
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

### More on the API

The `data` and `config` functions are optional. The properties that `config` returns defines the type of page. The default page is a build page.

Build pages don't have access to a request object.

The response that `render` returns is a tuple of `body, meta` where `meta` can have `status_code: int` and/or `headers: dict` keys e.g. `{"status_code": 200, "headers": {"some":"header"}}`.

### More on Packages

If you are using packages (i.e. more than just the standard library) you have to install them locally inside your project before building the project with the CLI.

e.g. with `pip` you can run `pip3 install -r requirements.txt --target .`.

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
