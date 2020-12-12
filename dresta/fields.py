"""
Marshmallow fields for api views
"""
import collections.abc
from marshmallow import fields, ValidationError, utils
import inspect

from typing import List


class RawCast(fields.Raw):
    """
    Casts the raw input to the given data type
    """
    def __init__(self, cast: type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cast = cast

    def cast(self, value):
        try:
            return self._cast(value)
        except Exception as e:
            raise ValidationError(str(e)) from e

    def _deserialize(self, value, attr, data, **kwargs):
        return self.cast(value)


class QueryDictRawCast(RawCast):
    """
    Takes the last item in the querydict, and casts it to the given data type
    """
    def _get_value(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, collections.Sequence):
            return value[-1]
        return value

    def _deserialize(self, value: List[str], attr, data, **kwargs):
        return super()._deserialize(
            self._get_value(value), attr, data, **kwargs
        )


class QueryDictBytesCast(QueryDictRawCast):

    default_error_messages = {
        "invalid": "Not a valid string."
    }

    def _deserialize(self, value: List[str], attr, data, **kwargs):
        value = self._get_value(value)
        if isinstance(value, str):
            value = value.encode('utf-8')
        if not isinstance(value, collections.ByteString):
            raise self.make_error("invalid")

        return self._output(value)


class QueryDictStringCast(QueryDictRawCast):

    default_error_messages = {
        "invalid": "Not a valid string.",
        "invalid_utf8": "Not a valid utf-8 string."
    }

    def _deserialize(self, value: List[str], attr, data, **kwargs):
        value = self._get_value(value)
        if not isinstance(value, (str, collections.ByteString)):
            raise self.make_error("invalid")
        try:
            return utils.ensure_text_type(value)
        except UnicodeDecodeError as error:
            raise self.make_error("invalid_utf8") from error


class QueryDictNumberCast(QueryDictRawCast):

    default_error_messages = {
        "invalid": "Not a valid number.",
        "too_large": "Number too large."
    }

    def _validated(self, value):
        if value is None:
            return None
        if value is True or value is False:
            raise self.make_error("invalid", input=value)
        try:
            return self._cast(value)
        except (TypeError, ValueError) as error:
            raise self.make_error("invalid", input=value) from error
        except OverflowError as error:
            raise self.make_error("too_large", input=value) from error

    def _deserialize(self, value, attr, data, **kwargs):
        return self._validated(self._get_value(value))


class QueryDictBooleanCast(QueryDictRawCast):

    default_error_messages = {
        "invalid": "Not a valid boolean."
    }

    def _validated(self, value):
        if not fields.Boolean.truthy:
            return bool(value)
        else:
            try:
                if value in fields.Boolean.truthy:
                    return True
                elif value in fields.Boolean.falsy:
                    return False
            except TypeError as error:
                raise self.make_error("invalid", input=value) from error
        raise self.make_error("invalid", input=value)

    def _deserialize(self, value, attr, data, **kwargs):
        return self.cast(self._validated(self._get_value(value)))


class NestedCast(fields.Nested):
    def __init__(self, cast: type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cast = cast

    def cast(self, value):
        try:
            sig = inspect.signature(self._cast)
            bound = sig.bind(**value)
            return self._cast(*bound.args, **bound.kwargs)
        except Exception as e:
            raise ValidationError(str(e)) from e

    def _deserialize(self, value, attr, data, **kwargs):
        return self.cast(super()._deserialize(value, attr, data, **kwargs))
