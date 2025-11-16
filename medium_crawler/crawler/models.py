from django.db import models
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=200)
    medium_username = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Blog(models.Model):
    title = models.CharField(max_length=500)
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='blogs')
    tags = models.ManyToManyField(Tag, related_name='blogs')
    medium_url = models.URLField(unique=True)
    published_date = models.DateTimeField(blank=True, null=True)
    crawled_at = models.DateTimeField(auto_now_add=True)
    claps_count = models.IntegerField(default=0)
    reading_time = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-published_date', '-crawled_at']
    
    def __str__(self):
        return f"{self.title} by {self.author.name}"


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(blank=True, null=True)
    crawled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-published_date']
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.blog.title[:50]}"


class SearchHistory(models.Model):
    tag_searched = models.CharField(max_length=100)
    search_time = models.DateTimeField(auto_now_add=True)
    results_count = models.IntegerField(default=0)
    crawl_duration = models.FloatField(help_text="Duration in seconds")
    
    class Meta:
        ordering = ['-search_time']
        verbose_name_plural = "Search Histories"
    
    def __str__(self):
        return f"Search for '{self.tag_searched}' - {self.results_count} results"


class CrawlStatus(models.Model):
    CRAWL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    tag = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=CRAWL_STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    blogs_found = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Crawl for '{self.tag}' - {self.status}"
