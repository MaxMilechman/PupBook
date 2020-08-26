import os
import secrets
import PIL
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flask_login import current_user
from PupBook import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    i = Image.open(form_picture)
    wpercent = (125/float(i.size[0]))
    hsize = int((float(i.size[1])*float(wpercent)))
    i = i.resize((125, hsize), PIL.Image.ANTIALIAS)
    i.save(picture_path)

    # To retain picture orientation while resizing
    # try:
    #     image = Image.open(form_picture)
    #     for orientation in ExifTags.TAGS.keys():
    #         if ExifTags.TAGS[orientation] == 'Orientation': break
    #     exif = dict(image._getexif().items())
    #
    #     if exif[orientation] == 3:
    #         image = image.rotate(180, expand=True)
    #     elif exif[orientation] == 6:
    #         image = image.rotate(270, expand=True)
    #     elif exif[orientation] == 8:
    #         image = image.rotate(90, expand=True)
    #
    #     image.thumbnail((125, 125), Image.ANTIALIAS)
    #     image.save(picture_path)
    # except:
    #     traceback.print_exc()

    prev_picture = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
    if os.path.exists(prev_picture) and prev_picture != os.path.join(current_app.root_path, 'static/profile_pics/default.jpg'):
        os.remove(prev_picture)

    return picture_fn


def save_picture_post(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/posts', picture_fn)

    i = Image.open(form_picture)
    wpercent = (300 / float(i.size[0]))
    hsize = int((float(i.size[1]) * float(wpercent)))
    i = i.resize((300, hsize), PIL.Image.ANTIALIAS)
    i.save(picture_path)

    return picture_fn


def save_picture_photos(form_picture):
    path = os.path.join(current_app.root_path, 'static/photos', current_user.username)

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(path, picture_fn)

    i = Image.open(form_picture)
    width = i.size[0]
    height = i.size[1]

    if width > height:
        difference = width - height
        offset = difference / 2
        resize = (offset, 0, width - offset, height)

    else:
        difference = height - width
        offset = difference / 2
        resize = (0, offset, width, height - offset)

    resized_image = i.crop(resize).resize((300, 300), Image.ANTIALIAS)
    resized_image.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)


