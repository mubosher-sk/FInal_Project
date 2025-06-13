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
    if request.method == 'POST':
        # Get form values
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        birth_date = request.form.get('birth_date')
        country_of_birth = request.form.get('country_of_birth')
        about = request.form.get('about')
        favourites = ""


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
            "about": about,
            "favourites": favourites
        })

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('home.home'))

    return render_template('register.html', countries=countries, current_year=date.today().isoformat())

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
            return redirect(url_for('home.home'))  # or your home/dashboard page
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
