# News Article RSS Feed Collector and Classifier

This project is a Python-based application that collects news articles from various RSS feeds, classifies them into predefined categories using Natural Language Processing (NLP), and stores them in a PostgreSQL database. It utilizes Celery for asynchronous task management and Redis as a message broker.

# Features
RSS Feed Parsing: Fetches news articles from multiple RSS feeds.

Text Classification: Categorizes news into four categories:

Terrorism/Protest/Political Unrest/Riot

Positive/Uplifting

Natural Disasters

Others

Asynchronous Processing: Uses Celery to handle article fetching and classification in the background.

Database Storage: Stores news articles in a PostgreSQL database without duplicates.

# Tech Stack
Python

Feedparser: For parsing RSS feeds.

SQLAlchemy: For interacting with PostgreSQL.

Celery: For managing the task queue.

Redis: As the message broker for Celery.

spaCy: For Natural Language Processing and text classification.

# Installation
Python 3.x

PostgreSQL

Redis


# How It Works
The script fetches news articles from predefined RSS feeds.

Each article is classified using spaCy NLP into one of the predefined categories.

Classified articles are then stored in a PostgreSQL database.
