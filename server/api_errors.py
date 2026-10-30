"""A consistent JSON shape for errors raised by DRF views and serializers."""

from math import ceil

from rest_framework.exceptions import Throttled, ValidationError
from rest_framework.views import exception_handler


def first_message(value):
    if isinstance(value, dict):
        return next((message for item in value.values() if (message := first_message(item))), '')
    if isinstance(value, (list, tuple)):
        return next((message for item in value if (message := first_message(item))), '')
    return str(value) if value is not None else ''


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    original = response.data
    if isinstance(exc, Throttled):
        wait = ceil(exc.wait) if exc.wait is not None else None
        response.data = {
            'detail': f'Too many requests. Please try again in {wait} seconds.' if wait is not None else 'Too many requests. Please try again later.',
            'code': 'throttled',
        }
        if wait is not None:
            response.data['retry_after'] = wait
    elif isinstance(exc, ValidationError):
        response.data = {
            'detail': first_message(original) or 'Please correct the submitted fields.',
            'code': 'validation_error',
            'errors': original,
        }
    else:
        detail = original.get('detail') if isinstance(original, dict) else original
        code = original.get('code') if isinstance(original, dict) else None
        response.data = {
            'detail': first_message(detail) or 'The request could not be completed.',
            'code': code or getattr(exc, 'default_code', 'request_error'),
        }
    return response
