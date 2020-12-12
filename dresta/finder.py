import importlib
import inspect

from django.apps import AppConfig, apps

from typing import List, Tuple


def load_app_module(app: AppConfig, module: str):
    """
    Load a module that belongs to an app

    :param app: app to import from
    :param module: module name

    :return: found module or None
    """
    relative = '.%s' % module
    try:
        return importlib.import_module(relative, package=app.name)
    except ImportError:
        return None


def find_members(module) -> List[Tuple[str, object]]:
    """
    Find all the members of a module

    :param module: module

    :return: all public members of the module
    """
    return [
        m for m in inspect.getmembers(module)
        if not m[0].startswith('__')
    ]


def get_app(name: str) -> AppConfig:
    """
    Get an app from its name

    :param name: app name

    :return: AppConfig
    """

    # Check if the app label is the last part of the name

    label = name.split('.')[-1]
    try:
        return apps.get_app_config(label)
    except LookupError:
        pass
    for app in apps.get_app_configs():
        if app.name == name:
            return app
    raise LookupError("No app exists with the name %s" % repr(name))
