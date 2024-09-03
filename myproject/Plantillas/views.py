from django.shortcuts import render, get_object_or_404, redirect
from .models import Plantilla
from .forms import PlantillaForm

def plantilla_list(request):
    plantillas = Plantilla.objects.all()
    return render(request, 'plantillas/plantilla_list.html', {'plantillas': plantillas})

def plantilla_create(request):
    if request.method == 'POST':
        form = PlantillaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('plantilla_list')
    else:
        form = PlantillaForm()
    return render(request, 'plantillas/plantilla_create.html', {'form': form})

def plantilla_edit(request, pk):
    plantilla = get_object_or_404(Plantilla, pk=pk)
    if request.method == 'POST':
        form = PlantillaForm(request.POST, instance=plantilla)
        if form.is_valid():
            form.save()
            return redirect('plantilla_list')
    else:
        form = PlantillaForm(instance=plantilla)
    return render(request, 'plantillas/plantilla_edit.html', {'form': form})

def plantilla_delete(request, pk):
    plantilla = get_object_or_404(Plantilla, pk=pk)
    if request.method == 'POST':
        plantilla.delete()
        return redirect('plantilla_list')
    return render(request, 'plantillas/plantilla_confirm_delete.html', {'plantilla': plantilla})
