from flask import Blueprint, abort, flash, render_template, request, redirect, url_for, session
import requests
from bson.objectid import ObjectId
from db import db  # Your MongoDB connection

home_bp = Blueprint('home', __name__)

@home_bp.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = {
        'id': session['user_id'],
        'username': session['username']
    }

    # Dummy sample books data
    books = [
        {
            'title': '1984',
            'genre': 'Dystopian',
            'description': 'A classic dystopian novel by George Orwell. Set in a totalitarian regime under constant surveillance.',
            'image': 'https://covers.openlibrary.org/b/id/7222246-L.jpg'
        },
        {
            'title': 'Sapiens',
            'genre': 'Non-fiction',
            'description': 'A brief history of humankind by Yuval Noah Harari exploring how humans evolved and shaped the world.',
            'image': 'https://covers.openlibrary.org/b/id/8370221-L.jpg'
        },
        {
            'title': 'To Kill a Mockingbird',
            'genre': 'Historical Fiction',
            'description': 'Harper Lee’s timeless story of racial injustice and moral growth in the American South.',
            'image': 'https://covers.openlibrary.org/b/id/8225631-L.jpg'
        },
        {
            'title': 'Harry Potter and the Sorcerer\'s Stone',
            'genre': 'Fantasy',
            'description': 'J.K. Rowling’s magical introduction to the wizarding world through the eyes of Harry Potter.',
            'image': 'https://covers.openlibrary.org/b/id/7884866-L.jpg'
        },
        {
            'title': 'The Hobbit',
            'genre': 'Fantasy',
            'description': 'J.R.R. Tolkien’s tale of Bilbo Baggins and his adventure through Middle-earth.',
            'image': 'https://covers.openlibrary.org/b/id/6979861-L.jpg'
        },
        {
            'title': 'Pride and Prejudice',
            'genre': 'Romance',
            'description': 'Jane Austen’s sharp commentary on manners and matrimonial ambitions in 19th century England.',
            'image': 'https://covers.openlibrary.org/b/id/8231994-L.jpg'
        },
        {
            'title': 'The Catcher in the Rye',
            'genre': 'Literary Fiction',
            'description': 'J.D. Salinger’s novel exploring teenage angst and alienation through the voice of Holden Caulfield.',
            'image': 'https://covers.openlibrary.org/b/id/8231856-L.jpg'
        },
        {
            'title': 'Brave New World',
            'genre': 'Science Fiction',
            'description': 'Aldous Huxley’s chilling vision of a technologically advanced future ruled by conditioning and control.',
            'image': 'https://covers.openlibrary.org/b/id/8772030-L.jpg'
        },
        {
            'title': 'Becoming',
            'genre': 'Biography',
            'description': 'Michelle Obama’s inspiring memoir about her life, values, and journey as First Lady of the U.S.',
            'image': 'https://covers.openlibrary.org/b/id/9258989-L.jpg'
        },
        {
            'title': 'The Alchemist',
            'genre': 'Adventure',
            'description': 'Paulo Coelho’s philosophical novel about following your dreams and listening to your heart.',
            'image': 'https://covers.openlibrary.org/b/id/8108691-L.jpg'
        },
        {
            'title': 'Atomic Habits',
            'genre': 'Self-Help',
            'description': 'James Clear offers practical strategies to form good habits, break bad ones, and master behavior change.',
            'image': 'https://covers.openlibrary.org/b/id/10587602-L.jpg'
        },
        {
            'title': 'Educated',
            'genre': 'Memoir',
            'description': 'Tara Westover’s powerful memoir of growing up in a strict and abusive household and her journey to education.',
            'image': 'https://covers.openlibrary.org/b/id/9257353-L.jpg'
        }
    ]

    user_doc = db.users.find_one({'_id': ObjectId(session['user_id'])})
    user_interests = user_doc.get('book_interests', []) if user_doc else []
    user_favourites = user_doc.get('favorites', []) if user_doc else []

    return render_template('home.html', user=user, books=books, user_interests=user_interests, favourites=user_favourites)


@home_bp.route('/browse')
def all_books():
    return render_template('browse.html')


@home_bp.route('/favourites')
def favourites():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_doc = db.users.find_one({'_id': ObjectId(session['user_id'])})
    favourites = user_doc.get('favourites', []) if user_doc else []
    return render_template('favourites.html', books=favourites)


@home_bp.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return render_template('search_results.html', query="", books=[])

    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)
    data = response.json()

    books = []
    for doc in data.get('docs', [])[:40]:
        title = doc.get('title', '')
        authors = doc.get('author_name', [])
        cover_id = doc.get('cover_i')
        work_key = doc.get('key')  # e.g. '/works/OL12345W'

        if not cover_id or len(title) > 100 or not authors:
            continue

        books.append({
            'title': title,
            'description': "By " + ", ".join(authors),
            'genre': ", ".join(doc.get('subject', [])[:2]) if doc.get('subject') else 'Unknown',
            'image': f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg",
            'work_key': work_key.replace('/works/', '')  # Just the key id for URL param
        })

    return render_template('search_results.html', query=query, books=books)


@home_bp.route('/add_favourite', methods=['POST'])
def add_favourite():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    book = {
        'title': request.form.get('title'),
        'image': request.form.get('image'),
        'description': request.form.get('description'),
        'genre': request.form.get('genre')
    }

    db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$addToSet': {'favourites': book}}
    )

    flash(f'Added "{book["title"]}" to your favourites!', 'success')
    return redirect(request.referrer or url_for('home.home'))

@home_bp.route('/book/<book_key>')
def book_detail(book_key):
    # The book_key here is the OpenLibrary work key id, e.g. OL12345W
    url = f"https://openlibrary.org/works/{book_key}.json"
    resp = requests.get(url)
    if resp.status_code != 200:
        abort(404)

    book_data = resp.json()
    # Optional: Fetch additional details like description, covers, authors
    cover_id = book_data.get('covers', [None])[0]
    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None

    # Format author names if available
    authors = []
    for author in book_data.get('authors', []):
        author_key = author.get('author', {}).get('key')
        if author_key:
            author_resp = requests.get(f"https://openlibrary.org{author_key}.json")
            if author_resp.status_code == 200:
                author_data = author_resp.json()
                authors.append(author_data.get('name'))

    description = book_data.get('description')
    if isinstance(description, dict):
        description = description.get('value')
    elif isinstance(description, str):
        pass
    else:
        description = "No description available."

    return render_template('book_detail.html',
                           book=book_data,
                           cover_url=cover_url,
                           authors=authors,
                           description=description)


@home_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('profile.html')
