from django.shortcuts import render

def reportes_home(request):
    return render(request, 'reportes/reportes_home.html')
