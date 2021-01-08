"""
Api Decorators
"""
from functools import update_wrapper

from . import views

from marshmallow import Schema

from typing import Optional, List, Type


def api(name: str = None, *,
        methods: Optional[List[str]] = None,
        allow_get_params: bool = True,
        auth_required: bool = False,
        args_schema: Optional[Type[Schema]] = None,
        schema: Optional[Type[Schema]] = None):
    """
    Create an api view

    :param method: allowed request method types
    :param allow_get_params: whether to allow GET parameters when the method
        is not GET
    :param schema: result schema
    :param args_schema: request schema
    :param auth_required: whether you need to be authenticated to access the
        api
    """

    def decorator(func: callable):
        obj = views.Api(
            func=func,
            methods=methods,
            allow_get_params=allow_get_params,
            auth_required=auth_required,
            args_schema=args_schema,
            schema=schema,
            name=name
        )
        return update_wrapper(obj, func)

    return decorator
