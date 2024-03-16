from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Meow meow black sheep.")


def home(request):
    return render(request, "ppredict/home.html")
