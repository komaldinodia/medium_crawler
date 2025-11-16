from django.urls import path
from . import views

app_name = 'crawler'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_tag, name='search_tag'),
    path('crawl/<str:tag_name>/', views.crawl_status, name='crawl_status'),
    path('api/crawl-progress/<str:tag_name>/', views.crawl_progress_api, name='crawl_progress_api'),
    path('blogs/', views.blog_list, name='blog_list'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('history/', views.search_history_view, name='search_history'),
    path('api/tag-suggestions/', views.tag_suggestions_api, name='tag_suggestions_api'),
]