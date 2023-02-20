import time


def render(data):
    return f"<h1>regenerate page: {data['time']}</h1>", {}


def data(request=None):
    return {
        "time": time.time()
    }


def config():
    return {
        "regenerate": {
            "every": 5
        }
    }
