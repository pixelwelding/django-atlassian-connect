from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def ajs(resize=True, size_to_parent=False, margin=True, base=False):
    data_options = "resize:{};sizeToParent:{};margin:{};base:{}".format(
        resize, size_to_parent, margin, base
    )
    script_str = "<script src='https://connect-cdn.atl-paas.net/all.js' data-options='{}'></script>".format(
        data_options
    )
    return mark_safe(script_str)
