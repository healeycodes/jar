import os
import glob
import json
import click
import shutil
import inspect
import importlib.util
from pathlib import Path
import distutils.dir_util


class Request:
    def __init__(self, method, path, headers, body):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body

    @staticmethod
    def from_event(event):
        event_body = json.loads(event['body'])
        return Request(
            event_body['method'],
            event_body['path'],
            event_body['headers'],
            event_body.get('body', None)
        )


def call_data(page, request=None):
    # the data function is optional
    if not (hasattr(page, 'data') and callable(page.data)):
        return {}

    # request is an optional arg for data()
    if len(inspect.getfullargspec(page.data).args) == 0:
        return page.data()
    else:
        return page.data(request)


def call_render(page, event=None):
    request = None
    if event:
        request = Request.from_event(event)

    data = call_data(page, request)

    # data is an optional arg for render()
    if len(inspect.getfullargspec(page.render).args) == 0:
        output, info = page.render()
    else:
        output, info = page.render(data)

    ret = {
        "statusCode": info.get('status_code', 200),
        "headers": {'Content-Type': 'text/html'},
        "body": "" if not output else output
    }
    ret['headers'] |= info.get('headers', {})

    return ret


def app(event, context):
    module_location = "__MODULE_LOCATION"

    spec = importlib.util.spec_from_file_location("", module_location)
    page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(page)

    return call_render(page, event)


def copy_files(source_dir, target_dir):
    distutils.dir_util.copy_tree(source_dir, target_dir)


def create_handler(path, module_location):
    # behold the power of metaprogramming
    with open(path, "w") as f:
        # imports
        f.write("import json\nimport inspect\nimport importlib.util\n")
        f.write('\n')
        # request class
        request_source = inspect.getsource(Request)
        f.write(request_source)
        f.write('\n')
        # call_data function
        call_data_source = inspect.getsource(call_data)
        f.write(call_data_source)
        f.write('\n')
        # call_render function
        call_render_source = inspect.getsource(call_render)
        f.write(call_render_source)
        f.write('\n')
        # app function
        app_source = inspect.getsource(app)
        f.write(app_source.replace("__MODULE_LOCATION", module_location))
        f.write('\n')


def build(root):
    root_path = os.path.normpath(root)
    build_dir = "build"

    # clear .vercel/output if it exists
    shutil.rmtree(os.path.join(build_dir, ".vercel/output"),
                  onerror=lambda lstat, path, info: None)

    # create directory structure
    Path(os.path.join(build_dir, ".vercel/output/static")).mkdir(parents=True)
    Path(os.path.join(build_dir, ".vercel/output/functions")).mkdir(parents=True)

    build_config = {
        'version': 3,
        'overrides': {},
    }

    # handle pages dir
    pages_dir = os.path.join(root, 'pages')
    if os.path.isdir(pages_dir):
        for file in glob.glob(os.path.join(pages_dir, "**/*.py"), recursive=True):
            # infer the request path from the file system path
            path_parts = file.split(os.sep)
            request_path_offset = len(root_path.split(os.sep)) + 1
            request_path_with_py = '/'.join(path_parts[request_path_offset:])
            request_path = request_path_with_py[: len(
                request_path_with_py) - len(".py")]

            # load the file
            spec = importlib.util.spec_from_file_location("", file)
            page = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(page)

            config = {}
            if hasattr(page, 'config') and callable(page.config):
                config = page.config()

            if not 'fresh' in config and not 'regenerate' in config:
                # build page
                build_page_path = os.path.join(
                    build_dir, f".vercel/output/static/{request_path}")
                build_page_parent_dir = os.sep.join(
                    build_page_path.split(os.sep)[:-1])
                # we might need to first create the parent dir
                Path(build_page_parent_dir).mkdir(parents=True, exist_ok=True)
                with open(os.path.join(build_dir, f".vercel/output/static/{request_path}"), "w") as f:
                    res = call_render(page)
                    f.write(res['body'])
                    build_config['overrides'][request_path] = {
                        'contentType': res['headers']['Content-Type']
                    }
                print(f"build page: /{request_path}")
            else:
                # fresh and regenerated pages need the same setup because they both output functions

                func_dir = os.path.join(
                    build_dir, f".vercel/output/functions/{request_path}.func")
                Path(func_dir).mkdir(parents=True)
                copy_files(root_path, func_dir)
                module_location = os.sep.join(
                    path_parts[path_parts.index("pages"):])
                create_handler(os.path.join(
                    func_dir, "__handler.py"), module_location)

                if 'fresh' in config:
                    # fresh page
                    print(f"fresh page: /{request_path}")
                elif 'regenerate' in config:
                    # regenerated page
                    every = config.get("regenerate", {}).get('every', None)
                    if not every:
                        raise Exception(
                            f"missing `every` key in regenerate config for: {file}"
                        )
                    fallback = config.get("fallback", True)

                    fallback_name = f"{request_path}.prerender-fallback"
                    if fallback:
                        with open(os.path.join(build_dir, '.vercel/output/functions', fallback_name), "w") as f:
                            res = call_render(page)
                            f.write(res['body'])
                            build_config['overrides'][request_path] = {
                                'contentType': res['headers']['Content-Type']
                            }

                    with open(os.path.join(build_dir, '.vercel/output/functions', f"{request_path}.prerender-config.json"), "w") as f:
                        prerender_config = {"expiration": every}
                        if fallback:
                            prerender_config["fallback"] = fallback_name
                        json.dump(prerender_config, f)
                    print(f"regenerate page: /{request_path}")

                with open(os.path.join(func_dir, ".vc-config.json"), "w") as f:
                    json.dump(
                        {
                            "handler": "__handler.app",
                            "runtime": "python3.9",
                            "environment": {},
                        },
                        f,
                    )

    # handle public dir
    public_dir = os.path.join(root, 'public')
    if os.path.isdir(public_dir):
        for file in glob.glob(os.path.join(public_dir, "**/*.*"), recursive=True):
            copy_to = os.path.join(
                build_dir, '.vercel/output/static/', os.path.basename(file))
            Path(os.path.dirname(copy_to)).mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, copy_to)
            print(
                f"public file: {copy_to[copy_to.index('output/static')+len('output/static'):]}")

    with open(os.path.join(build_dir, '.vercel/output/config.json'), 'w') as f:
        json.dump(build_config, f, sort_keys=True)


@click.command()
@click.argument("mode")
@click.argument("root", default=".")
def entry(mode, root):
    if mode != "build":
        raise Exception(f"unknown mode: {mode}")
    build(root)


if __name__ == "__main__":
    entry()
