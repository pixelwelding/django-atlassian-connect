from django.db import models


class SecurityContextManager(models.Manager):
    def get_by_natural_key(self, key, client_key, product_type):
        return self.get(key=key, client_key=client_key, product_type=product_type)
