from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def helloworld_macro(request):
    return render(request, "helloworld/macro.html")
