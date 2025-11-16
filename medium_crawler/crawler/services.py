import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from django.utils import timezone
from .models import Blog, Author, Tag, SearchHistory, CrawlStatus
import feedparser
from urllib.parse import quote


class MediumCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_by_tag(self, tag_name, limit=10):
        """
        Search Medium articles by tag using RSS feed
        """
        try:
            # Clean and encode the tag name properly
            clean_tag = tag_name.strip().lower().replace(' ', '-')
            encoded_tag = quote(clean_tag, safe='')
            rss_url = f"https://medium.com/feed/tag/{encoded_tag}"
            
            print(f"Fetching RSS from: {rss_url}")
            feed = feedparser.parse(rss_url)
            print(feed)
            if not feed.entries:
                return []
                
            articles = []
            for entry in feed.entries[:limit]:
                # Clean title from RSS artifacts
                title = entry.title
                title = re.sub(r'\?Source=Rss.*$', '', title, flags=re.IGNORECASE)
                title = re.sub(r'[A-F0-9]{12,}$', '', title).strip()
                
                # Extract author
                author = entry.get('author', 'Unknown Author')
                
                # Extract published date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_date = datetime(*entry.published_parsed[:6])
                        published_date = timezone.make_aware(published_date)
                    except:
                        published_date = timezone.now()
                
                # Extract content/summary
                content = entry.get('summary', '')
                if content:
                    content = BeautifulSoup(content, 'html.parser').get_text()
                
                articles.append({
                    'url': entry.link,
                    'title': title,
                    'author': author,
                    'content': content,
                    'published_date': published_date,
                    'tags': [tag_name]
                })
            
            return articles
            
        except Exception as e:
            print(f"Error fetching RSS feed for {tag_name}: {str(e)}")
            return []
    
    def crawl_article_content(self, article_url):
        """
        Extract full article content from Medium URL
        """
        try:
            response = self.session.get(article_url, timeout=15)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract full content from paragraphs
            content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            full_content = '\n\n'.join([elem.get_text().strip() 
                                      for elem in content_elements 
                                      if elem.get_text().strip()])
            
            # Extract reading time
            reading_time = 'Unknown'
            time_patterns = [
                r'\d+\s*min\s*read',
                r'\d+\s*minute\s*read'
            ]
            
            page_text = soup.get_text()
            for pattern in time_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    reading_time = match.group()
                    break
            
            # Extract claps count (basic attempt)
            claps_count = 0
            clap_patterns = [r'(\d+)\s*clap', r'(\d+)\s*applause']
            for pattern in clap_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        claps_count = int(match.group(1))
                        break
                    except:
                        pass
            
            return {
                'content': full_content,
                'reading_time': reading_time,
                'claps_count': claps_count
            }
            
        except Exception as e:
            print(f"Error extracting content from {article_url}: {str(e)}")
            return None
    
    def crawl_tag_articles(self, tag_name, limit=10, status_callback=None):
        """
        Crawl articles for a specific tag with real-time updates
        """
        start_time = time.time()
        
        crawl_status = CrawlStatus.objects.create(
            tag=tag_name,
            status='in_progress'
        )
        
        try:
            articles = self.search_by_tag(tag_name, limit)
            
            if not articles:
                crawl_status.status = 'completed'
                crawl_status.completed_at = timezone.now()
                crawl_status.blogs_found = 0
                crawl_status.error_message = "No articles found for this tag"
                crawl_status.save()
                return []
            
            crawled_blogs = []
            
            for i, article_data in enumerate(articles):
                if status_callback:
                    status_callback(f"Crawling {i+1}/{len(articles)}: {article_data['title'][:50]}...")
                
                # Get additional content
                additional_content = self.crawl_article_content(article_data['url'])
                
                if additional_content:
                    article_data.update(additional_content)
                
                # Save to database
                blog = self._save_article_data(article_data)
                if blog:
                    crawled_blogs.append(blog)
                
                # Respectful delay
                time.sleep(2)
            
            # Update status
            crawl_status.status = 'completed'
            crawl_status.completed_at = timezone.now()
            crawl_status.blogs_found = len(crawled_blogs)
            crawl_status.save()
            
            # Save search history
            duration = time.time() - start_time
            SearchHistory.objects.create(
                tag_searched=tag_name,
                results_count=len(crawled_blogs),
                crawl_duration=duration
            )
            
            return crawled_blogs
            
        except Exception as e:
            crawl_status.status = 'failed'
            crawl_status.error_message = str(e)
            crawl_status.completed_at = timezone.now()
            crawl_status.save()
            return []
    
    def _save_article_data(self, article_data):
        """
        Save article data to database
        """
        try:
            # Check if already exists
            if Blog.objects.filter(medium_url=article_data['url']).exists():
                return None
            
            # Get or create author
            author, created = Author.objects.get_or_create(
                name=article_data['author'],
                defaults={'medium_username': ''}
            )
            
            # Create blog
            content = article_data.get('content', '')
            summary = content[:300] + '...' if len(content) > 300 else content
            
            blog = Blog.objects.create(
                title=article_data['title'],
                content=content,
                summary=summary,
                author=author,
                medium_url=article_data['url'],
                published_date=article_data.get('published_date'),
                claps_count=article_data.get('claps_count', 0),
                reading_time=article_data.get('reading_time', 'Unknown')
            )
            
            # Add tags
            for tag_name in article_data.get('tags', []):
                tag, created = Tag.objects.get_or_create(name=tag_name.lower())
                blog.tags.add(tag)
            
            return blog
            
        except Exception as e:
            print(f"Error saving article: {str(e)}")
            return None
    
    def suggest_tags(self, query):
        """
        Suggest related tags based on query
        """
        existing_tags = Tag.objects.filter(name__icontains=query).values_list('name', flat=True)[:5]
        
        common_tags = [
            'technology', 'programming', 'python', 'javascript', 'data-science',
            'machine-learning', 'web-development', 'startup', 'business',
            'productivity', 'design', 'marketing', 'entrepreneurship',
            'artificial-intelligence', 'blockchain', 'software-engineering'
        ]
        
        suggested_tags = [tag for tag in common_tags if query.lower() in tag.lower()]
        all_suggestions = list(existing_tags) + suggested_tags
        
        return list(dict.fromkeys(all_suggestions))[:5]