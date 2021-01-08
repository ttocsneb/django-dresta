"""
Api Views
"""
from typing import Type, Optional, List
from marshmallow import Schema, ValidationError
import json
import inspect
import logging

from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.utils.log import log_response
from django.urls import path

from .utils import JsonEncoder

from .annotate import annotator
from . import parser

from .exceptions import APIError, ValidateError, USER_ERROR, SERV_ERROR


class Api:
    """
    Api Handler

    :param func: api function
    :param method: allowed request method types
    :param allow_get_params: whether to allow GET parameters when the method
        is not GET
    :param schema: result schema
    :param args_schema: request schema
    :param auth_required: whether you need to be authenticated to access the
        api
    """
    def __init__(self, **kwargs):
        self.func: callable = kwargs.pop('func')
        self.sig = inspect.signature(self.func)
        self.methods: Optional[List[str]] = kwargs.pop('methods', None)
        self.allow_get_params: bool = kwargs.pop('allow_get_params', True)
        self.args_schema: Type[Schema] = kwargs.pop('args_schema', None)
        self.schema: Optional[Type[Schema]] = kwargs.pop('schema', None)
        self.auth_required: bool = kwargs.pop('auth_required', False)
        self._name: Optional[str] = kwargs.pop('name', None)

        self.logger = logging.getLogger(__name__)

        if self.args_schema is None:
            self.args_schema = annotator.annotate(
                self.func,
                ignore=["request"]
            )

    @property
    def name(self):
        """
        The name of the api view
        """
        if self._name:
            return self._name
        else:
            return self.func.__name__

    @property
    def urlpattern(self):
        """
        The urlpattern for this view
        """
        return path("%s/" % self.name, self)

    def _merge(self, source, destination):
        """
        Recursive merge from source to destination

        :param source: source
        :param destination: destination

        :return: destination
        """
        for k, v in source.items():
            if isinstance(v, dict):
                node = destination.setdefault(k, {})
                if not isinstance(node, dict):
                    node = destination[k] = {}
                self._merge(v, node)
            else:
                destination[k] = v

        return destination

    def _api_error(self, request: HttpRequest, error: APIError):
        response = error.response()
        log_response(
            '%s (%s): %s', error.details, error.code, request.path,
            response=response,
            request=request
        )
        return response

    def __call__(self, request: HttpRequest):
        """
        The actual view of the api

        :param request: request
        """
        try:
            # Assert the correct method type
            if self.methods is not None and request.method not in self.methods:
                apiError = APIError(
                    USER_ERROR | 2,
                    detail="Method Not Allowed",
                    methods=self.methods
                )
                return self._api_error(request, apiError)

            # Get the GET params
            if (request.method != 'GET' and self.allow_get_params) \
                    or request.method == 'GET':
                params = parser.parseQueryDict(request.GET)
            else:
                params = {}

            # Get the POST params
            if request.body:
                try:
                    post = json.loads(request.body, encoding=request.encoding)
                    params = self._merge(post, params)
                except json.JSONDecodeError as error:
                    apiError = APIError(
                        USER_ERROR | 3,
                        detail="Invalid Json",
                        error=str(error)
                    )
                    return self._api_error(request, apiError)

            # Parse the arguments
            args_schema = self.args_schema()
            try:
                args = args_schema.load(params)
                if 'request' in self.sig.parameters:
                    args['request'] = request
                bound = self.sig.bind(**args)
            except ValidationError as error:
                apiError = ValidateError.fromMarshmallowError(
                    error,
                    detail="Invalid Parameters"
                )
                return self._api_error(request, apiError)

            if self.auth_required:
                # Assert authentication
                if not request.user.is_authenticated:
                    apiError = APIError(
                        USER_ERROR | 4,
                        "Authentication required."
                    )
                    raise self._api_error(request, apiError)

            # Run the api
            try:
                result = self.func(*bound.args, **bound.kwargs)
            except APIError as error:
                return self._api_error(request, error)

            # Dump the results
            if self.schema is not None:
                schema = self.schema()
                result = schema.dump(result)

            if result is None:
                result = {}

            return JsonResponse(result, encoder=JsonEncoder)
        except Exception:
            self.logger.exception("Internal Error")
            apiError = APIError(
                code=SERV_ERROR,
                detail="Internal Error"
            )
            return self._api_error(request, apiError)
