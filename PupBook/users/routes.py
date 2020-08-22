import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from PupBook import db, bcrypt
from PupBook.models import User, Post
from PupBook.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, ProfilePhotosForm
from PupBook.users.utils import save_picture, save_picture_photos, send_reset_email

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash(f'Login unsuccessful. Please check your email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


# @users.route("/account", methods=['GET', 'POST'])
# @login_required
# def account():
#     form = UpdateAccountForm()
#     if form.validate_on_submit():
#         if form.picture.data:
#             picture_file = save_picture(form.picture.data)
#             current_user.image_file = picture_file
#         current_user.username = form.username.data
#         current_user.email = form.email.data
#         db.session.commit()
#         flash('Your account has been updated!', 'success')
#         return redirect(url_for('users.account'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.email.data = current_user.email
#     image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
#     return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route("/profile/<string:username>")
@login_required
def profile(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(per_page=5, page=page)
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile.html', title='Profile', image_file=image_file, posts=posts, user=user)


@users.route("/profile/about", methods=['GET', 'POST'])
@login_required
def profile_about():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile_about.html', title='About', image_file=image_file, user=user)


@users.route("/profile/photos", methods=['GET', 'POST'])
@login_required
def profile_photos():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    form = ProfilePhotosForm()
    images = os.listdir(os.path.join(current_app.static_folder, 'photos', current_user.username))
    if form.validate_on_submit():
        for file in form.pictures.data:
            save_picture_photos(file)
        if len(form.pictures.data) > 1:
            flash('Your images has been uploaded!', 'success')
        else:
            flash('Your image has been uploaded!', 'success')
        return redirect(url_for('users.profile_photos'))
    return render_template('profile_photos.html', title='Photos', image_file=image_file, images=images, form=form, user=user)


@users.route("/profile/friends", methods=['GET', 'POST'])
@login_required
def profile_friends():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile_friends.html', title='Profile', image_file=image_file, user=user)


@users.route("/profile/account", methods=['GET', 'POST'])
@login_required
def profile_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.age = form.age.data
        current_user.breed = form.breed.data
        current_user.sex = form.sex.data
        current_user.current_city = form.current_city.data
        current_user.birthday = form.birthday.data
        current_user.favorite_food = form.favorite_food.data
        current_user.relationship = form.relationship.data
        current_user.interests = form.interests.data
        current_user.parents = form.parents.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.profile_account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.age.data = current_user.age
        form.breed.data = current_user.breed
        form.sex.data = current_user.sex
        form.current_city.data = current_user.current_city
        form.birthday.data = current_user.birthday
        form.favorite_food.data = current_user.favorite_food
        form.relationship.data = current_user.relationship
        form.interests.data = current_user.interests
        form.parents.data = current_user.parents
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile_account.html', title='Account', image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(per_page=5, page=page)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your passsword has been updated! You are now able to log in!', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
