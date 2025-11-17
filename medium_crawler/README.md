
### Prerequisites
- Python 3.8+ 
- Virtual environment
- Dependencies 

### Running the Application
### Create a working directory (optional)
```cmd
mkdir testing
cd testing/
```
### Clone the repository
```cmd
git clone https://github.com/komaldinodia/medium_crawler.git
```
### Move into the project directory
```cmd
cd medium_crawler/
```
### You should see a folder named medium_crawler inside

### Navigate into the actual project folder
```cmd
cd medium_crawler/
```
1. **Activate virtual environment** :
```cmd
python3 -m venv venv 
source venv/bin/activate
```
2. **Install Dependencies** :
```cmd
pip install -r requirements.txt
```
3. **run migrations**:
```cmd
python manage.py migrate
```

3. **Start the development server**:
```cmd
python manage.py runserver
```

3. **Access the application**:
- Main application: http://127.0.0.1:8000/
- Django Admin Panel: http://127.0.0.1:8000/admin/
  - Username: `admin`
  - Password: `admin123`

## 📋 Features Implemented

### Core Features (150 points)
- **Tag-based crawling**: Enter any tag to crawl Medium articles
- **Real-time updates**: Watch blogs appear as they're crawled (no page refresh)
- **Database storage**: All data stored with proper relationships
- **Bootstrap UI**: Responsive, professional interface
- **Admin panel**: Django admin for data management
- **Search history**: Track all previous searches
- **Blog management**: View, search, and filter crawled blogs

### Advanced Features
- **Tag suggestions**: Auto-suggest tags as you type
- **Error handling**: Graceful error handling and user feedback
- **Pagination**: Browse large sets of results easily
- **Responsive design**: Works on desktop and mobile
- **Progress tracking**: Visual progress bar during crawling


### 1. Crawl Medium Articles
1. Go to the home page (http://127.0.0.1:8000/)
2. Enter a tag name (e.g., "python", "javascript", "startup")
3. Click "Start Crawling"
4. Watch real-time updates as articles are crawled
5. View results and click through to full articles

### 2. Browse Crawled Articles  
- Visit "All Blogs" to see paginated list of all crawled articles
- Use search functionality to find specific articles
- Filter by tags using the dropdown
- Click on any article title to view full details

### 3. Admin Panel
- Access Django admin at http://127.0.0.1:8000/admin/
- Manage blogs, authors, tags, and comments
- View detailed crawl statistics
- Export data or perform bulk operations

### 4. Search History
- View "Search History" to see all previous crawl operations
- See crawl duration and results count for each search
- Re-run successful searches



