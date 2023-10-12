from operator import attrgetter
from django.shortcuts import render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from blog.models import BlogPost
from blog.views import get_blog_queryset


POSTS_PER_PAGE = 10

def home_screen_view(request):
    context = {}

    query = ""
    if request.GET:
        query = request.GET.get('q', '')
        context['query'] = str(query)

    posts = sorted(get_blog_queryset(query), key=attrgetter('date_updated'), reverse=True)
    
    
    # Pagination
    page = request.GET.get('page', 1)
    posts_paginator = Paginator(posts, POSTS_PER_PAGE)

    try:
        posts = posts_paginator.page(page)
    except PageNotAnInteger:
        posts = posts_paginator.page(POSTS_PER_PAGE)
    except EmptyPage:
        posts = posts_paginator.page(posts_paginator.num_pages)

    context['posts'] = posts

    return render(request, 'personal/home.html', context)