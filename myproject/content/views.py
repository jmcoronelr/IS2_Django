# content/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Content
from .forms import ContentForm

def content_edit(request, pk):
    content = get_object_or_404(Content, pk=pk)
    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            return redirect('content_list')
    else:
        form = ContentForm(instance=content)
    return render(request, 'content/content_form.html', {'form': form})
def content_detail(request, pk):
    content = get_object_or_404(Content, pk=pk)
    return render(request, 'content/content_detail.html', {'content': content})


# content/views.py
def content_list(request):
    contents = Content.objects.all()
    return render(request, 'content/content_list.html', {'contents': contents})

def content_create(request):
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('content_list')
    else:
        form = ContentForm()
    return render(request, 'content/content_form.html', {'form': form})

def content_delete(request, pk):
    content = get_object_or_404(Content, pk=pk)
    if request.method == 'POST':
        content.delete()
        return redirect('content_list')
    return render(request, 'content/content_confirm_delete.html', {'content': content})
