from django.shortcuts import render,redirect
from django.urls import reverse


def home(request):
    if request.user.is_authenticated: #redirecciona en relacion al estado de autenticacion
        return redirect('sistema')
    return render(request, 'home.html')

def sistema(request):
    if not (request.user.is_authenticated): #redirecciona en relacion al estado de autenticacion
        return redirect('home')
    return render(request, 'sistema.html')