from blog import app, db, bcrypt
from flask import render_template, url_for, redirect, flash
from blog.forms import RegistrationForm, LoginForm
from blog.models import User, Post

posts = [
    {
        'author' : 'David',
        'title' : 'Blog Post 1',
        'content' : 'First post content',
        'date_posted' : 'April 20, 2023'
    },
    {
        'author' : 'John',
        'title' : 'Blog Post 2',
        'content' : 'Second post content',
        'date_posted' : 'April 21, 2023'
    },
    {
        'author' : 'Jane',
        'title' : 'Blog Post 3',
        'content' : 'Third post content',
        'date_posted' : 'April 22, 2023'
    }
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data} ! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'adminblog@example.com' and form.password.data == 'password':
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)