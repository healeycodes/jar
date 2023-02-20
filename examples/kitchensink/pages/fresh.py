import json
import time


def render(data):
    return f"<h1>fresh page {data['time']}</h1><code>{data['request']}</code>", {}


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
