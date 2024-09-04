from django.shortcuts import render,redirect
from django.urls import reverse


def home(request):
    return render(request, 'home.html')

def sistema(request):
    return render(request, 'sistema.html')