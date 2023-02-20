def render(data):
    return f"<h1>{data['text']}</h1>", {}


def data():
    return {
        "text": "I'm a nested path"
    }
