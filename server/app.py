#!/usr/bin/env python3

from flask import Flask, jsonify, session
from flask_migrate import Migrate
from models import db, Article, User
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Route to clear session page views
@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

# Route to show articles
@app.route('/articles/<int:id>')
def show_article(id):
    # Initialize page views if not already set
    session['page_views'] = session.get('page_views', 0)

    # Increment page views
    session['page_views'] += 1

    # If more than 3 articles have been viewed, return 401
    if session['page_views'] > 3:
        return jsonify({'message': 'Maximum pageview limit reached'}), 401

    # Fetch the article by ID
    article = Article.query.get(id)
    if not article:
        return {'message': 'Article not found'}, 404

    # Fetch the author
    author = User.query.get(article.user_id)

    # Create a preview of the article content (first 50 characters)
    preview = article.content[:50] + "..." if len(article.content) > 50 else article.content

    # Calculate estimated reading time based on article content length
    words = len(article.content.split())
    minutes_to_read = max(1, words // 200)  # 200 words per minute estimate

    # Return the article data as a JSON response
    return jsonify({
        'id': article.id,
        'title': article.title,
        'content': article.content,
        'author': author.name if author else 'Unknown',  # Default to 'Unknown' if no author
        'preview': preview,
        'minutes_to_read': minutes_to_read,
        'date': article.date.strftime('%Y-%m-%d') if article.date else None
    }), 200

if __name__ == '__main__':
    app.run(port=5555)
