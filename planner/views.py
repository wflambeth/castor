from django.shortcuts import HttpResponse, render

def index(request):
    return HttpResponse("Hello! This will soon be an excellent scheduler app.")
