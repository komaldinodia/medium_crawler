from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Blog, Tag, SearchHistory, CrawlStatus
from .services import MediumCrawler
from .forms import TagSearchForm
import json
import threading


def home(request):
    """Home page with search form and recent blogs"""
    form = TagSearchForm()
    recent_blogs = Blog.objects.all()[:10]
    search_history = SearchHistory.objects.all()[:5]
    
    context = {
        'form': form,
        'recent_blogs': recent_blogs,
        'search_history': search_history,
    }
    return render(request, 'crawler/home.html', context)


def search_tag(request):
    """Handle tag search and initiate crawling"""
    if request.method == 'POST':
        form = TagSearchForm(request.POST)
        if form.is_valid():
            tag_name = form.cleaned_data['tag_name'].strip().lower()
            
            # Start crawling in background thread
            crawler = MediumCrawler()
            
            # Create a unique identifier for this crawl session
            crawl_id = f"crawl_{tag_name}_{request.session.session_key}"
            request.session['current_crawl_id'] = crawl_id
            
            # Start background crawling
            thread = threading.Thread(
                target=background_crawl,
                args=(tag_name, crawl_id)
            )
            thread.daemon = True
            thread.start()
            
            return redirect('crawler:crawl_status', tag_name=tag_name)
    
    return redirect('crawler:home')


def background_crawl(tag_name, crawl_id):
    """Background function to crawl articles"""
    crawler = MediumCrawler()
    try:
        crawler.crawl_tag_articles(tag_name, limit=10)
    except Exception as e:
        print(f"Error in background crawl: {str(e)}")


def crawl_status(request, tag_name):
    """Show crawl status page with real-time updates"""
    context = {
        'tag_name': tag_name,
    }
    return render(request, 'crawler/crawl_status.html', context)


def crawl_progress_api(request, tag_name):
    """API endpoint to get crawl progress"""
    try:
        # Get latest crawl status for this tag
        crawl_status = CrawlStatus.objects.filter(tag=tag_name).first()
        
        if not crawl_status:
            return JsonResponse({
                'status': 'not_found',
                'message': 'Crawl not found'
            })
        
        # Get currently crawled blogs for this tag
        blogs = Blog.objects.filter(
            tags__name__iexact=tag_name,
            crawled_at__gte=crawl_status.started_at
        ).order_by('-crawled_at')
        
        blogs_data = []
        for blog in blogs:
            blogs_data.append({
                'title': blog.title,
                'author': blog.author.name,
                'summary': blog.summary or blog.content[:200] + '...',
                'url': blog.medium_url,
                'published_date': blog.published_date.strftime('%Y-%m-%d') if blog.published_date else 'Unknown',
                'reading_time': blog.reading_time,
                'tags': [tag.name for tag in blog.tags.all()],
            })
        
        return JsonResponse({
            'status': crawl_status.status,
            'blogs_found': len(blogs_data),
            'blogs': blogs_data,
            'total_expected': 10,
            'completed_at': crawl_status.completed_at.isoformat() if crawl_status.completed_at else None,
            'error_message': crawl_status.error_message,
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


def blog_list(request):
    """Display paginated list of all blogs"""
    blogs = Blog.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        blogs = blogs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__name__icontains=search_query)
        )
    
    # Tag filtering
    tag_filter = request.GET.get('tag')
    if tag_filter:
        blogs = blogs.filter(tags__name__iexact=tag_filter)
    
    # Pagination
    paginator = Paginator(blogs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all tags for filter dropdown
    all_tags = Tag.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'tag_filter': tag_filter,
        'all_tags': all_tags,
    }
    return render(request, 'crawler/blog_list.html', context)


def blog_detail(request, blog_id):
    """Display detailed view of a single blog"""
    blog = get_object_or_404(Blog, id=blog_id)
    comments = blog.comments.all()
    
    # Get related blogs based on tags
    if blog.tags.exists():
        related_blogs = Blog.objects.filter(
            tags__in=blog.tags.all()
        ).exclude(id=blog.id).distinct()[:3]
    else:
        related_blogs = Blog.objects.exclude(id=blog.id)[:3]
    
    context = {
        'blog': blog,
        'comments': comments,
        'related_blogs': related_blogs,
    }
    return render(request, 'crawler/blog_detail.html', context)


def search_history_view(request):
    """Display search history"""
    history = SearchHistory.objects.all()
    
    paginator = Paginator(history, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'crawler/search_history.html', context)


def tag_suggestions_api(request):
    """API endpoint to get tag suggestions"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    crawler = MediumCrawler()
    suggestions = crawler.suggest_tags(query)
    
    return JsonResponse({'suggestions': suggestions})
