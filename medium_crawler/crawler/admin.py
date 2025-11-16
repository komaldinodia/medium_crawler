from django.contrib import admin
from .models import Blog, Author, Tag, Comment, SearchHistory, CrawlStatus


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'medium_username', 'created_at')
    search_fields = ('name', 'medium_username')
    list_filter = ('created_at',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'blog_count')
    search_fields = ('name',)
    list_filter = ('created_at',)
    
    def blog_count(self, obj):
        return obj.blogs.count()
    blog_count.short_description = 'Blog Count'


@admin.register(Blog)  
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date', 'crawled_at', 'claps_count')
    list_filter = ('published_date', 'crawled_at', 'tags')
    search_fields = ('title', 'content', 'author__name')
    readonly_fields = ('crawled_at', 'medium_url')
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author').prefetch_related('tags')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'blog', 'published_date', 'crawled_at')
    list_filter = ('published_date', 'crawled_at')
    search_fields = ('author_name', 'content', 'blog__title')
    readonly_fields = ('crawled_at',)


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('tag_searched', 'results_count', 'crawl_duration', 'search_time')
    list_filter = ('search_time',)
    search_fields = ('tag_searched',)
    readonly_fields = ('search_time',)
    
    def has_add_permission(self, request):
        return False


@admin.register(CrawlStatus)
class CrawlStatusAdmin(admin.ModelAdmin):
    list_display = ('tag', 'status', 'blogs_found', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at')
    search_fields = ('tag',)
    readonly_fields = ('started_at', 'completed_at')
    
    def has_add_permission(self, request):
        return False
