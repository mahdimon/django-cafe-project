from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse

def staff_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_staff, login_url='staff:login')(view_func)
    return decorated_view_func
