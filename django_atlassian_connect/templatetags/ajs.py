from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def ajs(resize=True, size_to_parent=False, margin=True, base=False):
    def _to_js(val):
        if val:
            return "true"
        else:
            return "false"

    resize_str = _to_js(resize)
    size_to_parent_str = _to_js(size_to_parent)
    margin_str = _to_js(margin)
    base_str = _to_js(base)

    data_options = "resize:{};sizeToParent:{};margin:{};base:{}".format(
        resize_str, size_to_parent_str, margin_str, base_str
    )
    script_str = "<script src='https://connect-cdn.atl-paas.net/all.js' data-options='{}'></script>".format(
        data_options
    )
    return mark_safe(script_str)
