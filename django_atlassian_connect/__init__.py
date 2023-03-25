from django.utils.module_loading import autodiscover_modules


def autodiscover():
    autodiscover_modules("properties")
    autodiscover_modules("fields")
    autodiscover_modules("links")
    autodiscover_modules("issues")
