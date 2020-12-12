"""
Exceptions that can be raised in an api function
"""
import json
from django.http.response import JsonResponse

from marshmallow import ValidationError


class APIError(Exception):
    """
    The base exception for all api exceptions
    """
    def __init__(self, code: int = 400, detail: str = "API Error", **kwargs):
        self.code = code
        self.detail = detail
        self.details = kwargs
        self.details.update({
            'code': code,
            'detail': detail
        })

    def response(self):
        return JsonResponse(self.details)

    def __str__(self):
        return json.dumps(self.details)

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(
                '{}={}'.format(k, repr(v))
                for k, v in self.details.items()
            )
        )


class NotFoundError(APIError):
    """
    An error when something was not found
    """
    def __init__(self, code: int = 404, detail: str = "Not Found Error", **kwargs):
        super().__init__(code, detail, **kwargs)


class ValidateError(APIError):
    """
    An error when something could not be validated
    """
    def __init__(self, validation: list, code: int = 400, detail: str = "Validation Error", **kwargs):
        super().__init__(code, detail, validation=validation, **kwargs)

    @classmethod
    def fromMarshmallowError(cls, validation: ValidationError, **kwargs):
        """
        Create a Validation error from a marshmallow validation error

        :param validation: Validation Error
        """
        return cls(validation.messages, **kwargs)
