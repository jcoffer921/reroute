from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import BlogPost

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    return render(request, 'blog/detail.html', {'post': post})

