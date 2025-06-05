# routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import pycountry
from db import db  # the MongoDB db instance from app.py
from datetime import date

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    countries = sorted([country.name for country in pycountry.countries])
    BOOK_GENRES = [
        "Fiction", "Non-Fiction", "Science Fiction", "Fantasy",
        "Mystery", "Romance", "Biography", "History", "Self-Help", "Comics"
    ]
    if request.method == 'POST':
        # Get form values
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        birth_date = request.form.get('birth_date')
        country_of_birth = request.form.get('country_of_birth')
        book_interests = request.form.getlist('book_interests[]')
        about = request.form.get('about')

        # Check if user already exists
        if db.users.find_one({"email": email}):
            flash('Email address already exists', 'danger')
            return redirect(url_for('auth.register'))


        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert new user into DB
        db.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password,
            "birth_date": birth_date,
            "country_of_birth": country_of_birth,
            "book_interests": book_interests,
            "about": about
        })

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.home'))

    return render_template('register.html', countries=countries, book_genres=BOOK_GENRES, current_year=date.today().isoformat())

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.users.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            # Successful login: store user info in session
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('auth.home'))  # or your home/dashboard page
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))  # redirect if not logged in
    user = {
        'id': session['user_id'],
        'username': session['username']
    }

    books = [
        {
            'title': '1984',
            'genre': 'Dystopian',
            'description': 'A classic dystopian novel by George Orwell.',
            'image': 'https://covers.openlibrary.org/b/id/7222246-L.jpg'
        },
        {
            'title': 'The Great Gatsby',
            'genre': 'Classic',
            'description': 'A novel written by F. Scott Fitzgerald.',
            'image': 'https://covers.openlibrary.org/b/id/8226191-L.jpg'
        },
        {
            'title': 'Sapiens',
            'genre': 'Non-fiction',
            'description': 'A brief history of humankind by Yuval Noah Harari.',
            'image': 'https://covers.openlibrary.org/b/id/8370221-L.jpg'
        }
    ]

    # Optional: fetch user interests from DB
    user_doc = db.users.find_one({'_id': ObjectId(session['user_id'])})
    user_interests = user_doc.get('book_interests') if user_doc else []

    return render_template('home.html', user=user, books=books, user_interests=user_interests)

@auth_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('profile.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
