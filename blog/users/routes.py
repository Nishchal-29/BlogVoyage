from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import current_user, login_required
from blog import db
from blog.models import User, Post
from blog.users.forms import UpdateAccountForm
from blog.users.utils import save_picture

users = Blueprint('users', __name__)

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        db.session.commit()
        flash('Your account has been updated!', 'success')
        
        return redirect(url_for('users.account'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    
    return render_template('user_posts.html', posts=posts, user=user)