from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello,. You're at deal finders search option.")


# command for migration
# python manage.py makemigrations search_filter