"""
Api Decorators
"""
from functools import update_wrapper

from . import views


def api(**kwargs):
    """
    Create an api view

    :param method: allowed request method types
    :param allow_get_params: whether to allow GET parameters when the method
        is not GET
    :param schema: result schema
    :param args_schema: request schema
    """

    def decorator(func: callable):
        obj = views.Api(func=func, **kwargs)
        return update_wrapper(obj, func)

    return decorator
