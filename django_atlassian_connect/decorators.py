# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import wraps


def jwt_required(view_func):
    """
    Make the function be validated through JWTAuthenticationMiddleware and processed if the JWT is valid or raise a PermissionDenied if not.
    """

    def decorator(*args, **kwargs):
        return view_func(*args, **kwargs)

    decorator.jwt_required = True
    return wraps(view_func)(decorator)


def jwt_qsh_exempt(view_func):
    """
    Mark a view function as being exempt from the qsh claim protection.
    In practice this means that the actual path requested along with the query parameters won't be checked by the JWTAuthenticationMiddleware.
    """

    def decorator(*args, **kwargs):
        return view_func(*args, **kwargs)

    decorator.jwt_qsh_exempt = True
    return wraps(view_func)(decorator)
