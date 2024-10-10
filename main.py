import feedparser
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from celery import Celery
import spacy
import logging

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize spaCy
nlp = spacy.load("en_core_web_sm")

# Define Celery app
app = Celery('news_processor', broker='redis://localhost:6379/0')

# Database setup
DATABASE_URL = "postgresql://username:password@localhost:5432/news_db"  # Use your actual DB credentials
Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = 'news_articles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), unique=True)
    content = Column(Text)
    published_date = Column(DateTime)
    source_url = Column(String(255))
    category = Column(String(50))

# Initialize database connection and session
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Function to fetch RSS feed
def fetch_rss_feed(feed_url):
    try:
        feed = feedparser.parse(feed_url)
        articles = []
        for entry in feed.entries:
            # Handle missing or malformed date
            try:
                published_date = datetime(*entry.published_parsed[:6])
            except Exception:
                published_date = datetime.now()  # Default to current time if date is missing

            article = {
                'title': entry.title,
                'content': entry.summary,
                'published_date': published_date,
                'source_url': entry.link
            }
            articles.append(article)
        return articles
    except Exception as e:
        logger.error(f"Error fetching {feed_url}: {str(e)}")
        return []

# Function to store articles in the database
def store_article(article):
    if not session.query(NewsArticle).filter_by(title=article['title']).first():
        new_article = NewsArticle(**article)
        session.add(new_article)
        session.commit()

# Function to classify text using spaCy
def classify_text(content):
    doc = nlp(content)
    if "protest" in content.lower() or "riot" in content.lower():
        return "Terrorism/Protest/Political Unrest/Riot"
    elif "earthquake" in content.lower() or "flood" in content.lower():
        return "Natural Disasters"
    elif "happy" in content.lower() or "positive" in content.lower():
        return "Positive/Uplifting"
    else:
        return "Others"

# Celery task to process articles
@app.task
def process_articles():
    rss_feeds = [
        'http://rss.cnn.com/rss/cnn_topstories.rss',
        'http://qz.com/feed',
        'http://feeds.foxnews.com/foxnews/politics',
        'http://feeds.reuters.com/reuters/businessNews',
        'http://feeds.feedburner.com/NewshourWorld',
        'https://feeds.bbci.co.uk/news/world/asia/india/rss.xml'
    ]

    all_articles = []
    for feed in rss_feeds:
        all_articles.extend(fetch_rss_feed(feed))

    for article in all_articles:
        article['category'] = classify_text(article['content'])
        store_article(article)
        logger.info(f"Stored article: {article['title']} under category: {article['category']}")

if __name__ == '__main__':
    logger.info("Running RSS feed processor (for debugging).")
    process_articles()  # Optional: Directly run for testing, not with Celery.
