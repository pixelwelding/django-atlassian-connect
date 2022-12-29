from django.conf import settings
from django.test import TestCase, override_settings

from django_atlassian_connect.decorators import jwt_qsh_exempt, jwt_required


class JWTRequiredDecoratorTests(TestCase):
    def test_func(self):
        def view(request):
            pass

        decorated_view = jwt_required(view)
        self.assertTrue(decorated_view.jwt_required)

    def test_func_decorator(self):
        @jwt_required
        def view(request):
            pass

        self.assertTrue(view.jwt_required)


class JWTQshExemptTests(TestCase):
    def test_func_decorator(self):
        @jwt_qsh_exempt
        def view(request):
            pass

        self.assertTrue(view.jwt_qsh_exempt)
