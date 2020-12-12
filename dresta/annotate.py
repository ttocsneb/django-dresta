"""
Annotate functions into Marshmallow Schemas
"""
import inspect

import collections.abc
from marshmallow import Schema, fields

from typing import Type, List

from . import fields as api_fields


class Annotator:
    """
    Annotates functions into Schemas
    """
    annotations = [
        (inspect._empty, fields.Raw),
        (int, api_fields.QueryDictNumberCast),
        (float, api_fields.QueryDictNumberCast),
        (bool, api_fields.QueryDictBooleanCast),
        (str, api_fields.QueryDictStringCast),
        (collections.ByteString, api_fields.QueryDictBytesCast),
        (collections.Sequence, api_fields.RawCast),
        (collections.Set, api_fields.RawCast),
        (collections.Mapping, api_fields.RawCast),
    ]

    def __init__(self):
        self._registered_schemas = {}
        self._building_schemas = set()

    def _annotate_param(self, parameter: inspect.Parameter) -> fields.Field:
        """
        Annotate a field

        :param parameter: parameter

        :return: annotated field
        """
        params = {}
        if parameter.default == inspect._empty:
            params['required'] = True
        else:
            params['missing'] = parameter.default

        # Deal with Schemas inside Schemas
        if parameter.annotation in self._building_schemas:
            return api_fields.NestedCast(
                parameter.annotation,
                lambda: self._registered_schemas[parameter.annotation](),
                **params
            )

        # Simple types
        for t, f in self.annotations:
            if issubclass(parameter.annotation, t):
                return f(parameter.annotation, **params)

        # Advanced types
        try:
            return api_fields.NestedCast(
                parameter.annotation,
                self._registered_schemas[parameter.annotation],
                **params
            )
        except KeyError:
            # Create a new annotation
            return api_fields.NestedCast(
                parameter.annotation,
                self.annotate(parameter.annotation),
                **params
            )

    def annotate(self, func: callable, ignore: List[str] = []) -> Type[Schema]:
        """
        Annotate the function into a schema

        :param func: function to annotate
        :param ignore: arguments to ignore

        :return: schema for the function
        """
        if func in self._registered_schemas:
            return self._registered_schemas[func]
        self._building_schemas.add(func)
        sig = inspect.signature(func)
        params = {}
        for param in sig.parameters.values():
            if param.name in ignore:
                continue
            params[param.name] = self._annotate_param(param)

        schema = Schema.from_dict(params, name=func.__name__)

        self._building_schemas.remove(func)
        self._registered_schemas[func] = schema

        return schema


annotator = Annotator()
