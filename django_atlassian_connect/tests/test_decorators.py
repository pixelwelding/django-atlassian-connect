from django.conf import settings
from django.test import TestCase, override_settings

from django_atlassian_connect.decorators import (
    enable_licensing,
    jwt_qsh_exempt,
    jwt_required,
)


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


class EnableLicensingTests(TestCase):
    @override_settings(ENABLE_LICENSING=True)
    def test_func_decorator(self):
        @enable_licensing(settings.ENABLE_LICENSING)
        def view(request):
            pass

        self.assertTrue(view.enable_licensing)
