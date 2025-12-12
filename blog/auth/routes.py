import os
import requests
import secrets
from dotenv import load_dotenv
from flask import render_template, url_for, flash, redirect, request, Blueprint, session, abort
from flask_login import login_user, current_user, logout_user
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from blog import db, bcrypt
from blog.models import User
from blog.auth.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from blog.auth.utils import send_reset_email

load_dotenv()
auth = Blueprint('auth', __name__)

if os.getenv("DEBUG") == 'TRUE':
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

client_config = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": "https://blogvoyage-3.onrender.com/callback"
    }
}

flow = Flow.from_client_config(
    client_config=client_config,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://blogvoyage-3.onrender.com/callback"
)

@auth.route("/google_login")
def google_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@auth.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500)
        
    credentials = flow.credentials
    request_session = requests.session()
    
    token_request = google_requests.Request(session=request_session)
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=credentials.client_id,
        clock_skew_in_seconds=10
    )
    
    google_email = id_info.get("email")
    google_name = id_info.get("name")
    
    user = User.query.filter_by(email=google_email).first()
    
    if user:
        login_user(user, remember=True)
        flash(f'Welcome back, {user.username}!', 'success')
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        else:
            return redirect(url_for('main.home'))
        
    else:
        random_password = secrets.token_hex(16)
        hashed_password = bcrypt.generate_password_hash(random_password).decode('utf-8')
        
        new_user = User(
            username=google_name,
            email=google_email,
            password=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        flash(f'Account created for {google_name}! Welcome to BlogVoyage.', 'success')
        return redirect(url_for('main.home'))

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account created for {form.username.data} ! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='Register', form=form)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('main.home'))
            
        else:
            flash('Login failed. Please check your email and password.', 'danger')
            
    return render_template('login.html', title='Login', form=form)

@auth.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@auth.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_request.html', title='Reset Password', form=form)

@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_token.html', title='Reset Password', form=form)