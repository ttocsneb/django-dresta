"""
Exceptions that can be raised in an api function
"""
import json
from django.http.response import JsonResponse

from marshmallow import ValidationError


USER_ERROR = 0b0001_0000
'''An error caused by the user.'''
SERV_ERROR = 0b0010_0000
'''An error caused by the server.'''
VALI_ERROR = 0b0100_0000
'''An error that involves validation.'''


class APIError(Exception):
    """
    The base exception for all api exceptions
    """
    def __init__(self, code: int, detail: str = "API Error", **kwargs):
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
    NOT_FOUND = USER_ERROR | 1

    def __init__(self, code: int = NOT_FOUND, detail: str = "Not Found Error", **kwargs):
        super().__init__(code, detail, **kwargs)


class ValidateError(APIError):
    """
    An error when something could not be validated
    """
    NOT_FOUND = VALI_ERROR | 2

    def __init__(self, validation: list, code: int = NOT_FOUND, detail: str = "Validation Error", **kwargs):
        super().__init__(code, detail, validation=validation, **kwargs)

    @classmethod
    def fromMarshmallowError(cls, validation: ValidationError, **kwargs):
        """
        Create a Validation error from a marshmallow validation error

        :param validation: Validation Error
        """
        return cls(validation.messages, **kwargs)
