import os
import time
import md5
import base64
import datetime
from flask import Blueprint, request, render_template
from flask import flash, g, session, redirect, url_for
from flask import jsonify, abort, make_response
from flask import current_app
from flask_mail import Message
from werkzeug import check_password_hash, generate_password_hash
from werkzeug import secure_filename
from app import db
from app import mail
from app.users.forms import RegisterForm, LoginForm, ProfileForm, ForgotForm
from app.users.constants import UPLOAD_FOLDER
from app.users.models import User
from app.users.utils import allowed_image_file
from app.users.decorators import login_required, templated


mod = Blueprint('users', __name__, url_prefix='/users')


def authorize(user):
    session['user_id'] = user.id

def is_logged():
    return g.user


@mod.before_app_request
def before_request():
    """
    pull user's profile from the database before every request are treated
    """
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@mod.route('/dashboard')
@mod.route('/home')
@login_required
def home():
    return render_template(
        "users/me.html", user=g.user,
        form=form
    )

@mod.route('/pleaseconfirm')
def pleaseconfirm():
    if g.user:
        send_confirmation()
    return render_template("users/pleaseconfirm.html", user=g.user)


@mod.route("/confirm/<string:code>", methods=['GET', 'POST'])
def confirm(code):
    """docstring for reconfirm"""
    id = "{%s}" % base64.b64decode(code)
    try:
        user = db.session.query(User).get(id)
    except Exception:
        abort(404)

    if user.is_confirmed():
        abort(404)

    user.confirmed = 1
    user.active = 1
    db.session.commit()

    return redirect(url_for('users.home'))


@mod.route("/reconfirm/<string:alias>", methods=['GET', 'POST'])
def reconfirm(alias):
    """docstring for reconfirm"""
    if g.user:
        send_confirmation()
    return redirect(url_for('users.home'))


def send_confirmation():
    """docstring for send_confirmation"""

    lnk = url_for(
        'users.confirm',
        code=base64.b64encode(str(g.user.id)),
        _external=True
    )

    conflnk_html = '<a href="%s">%s</a>' % (
        lnk,
        lnk
    )

    msg = Message(
        "Please confirm your account at vision website",
        sender="noreply@.com",
        recipients=[g.user.get_email()]
    )
    msg.body = "\nWelcome\n\n"
    msg.body += "\nPlease confirm your account by clicking this link:\n"
    msg.body += "\n%s" % lnk
    msg.body += "\nFuture notifications will be sent to this email address."
    msg.body += "\nThank you,"
    msg.body += "\n\nTeam."

    msg.html = "Hi, Welcome"
    msg.html += "<br><br>Please confirm your account by clicking this link:"
    msg.html += "\n%s" % conflnk_html
    msg.html += "<br>Future notifications will be sent to this email address."
    msg.html += "<br>Thank you,"
    msg.html += "<br><br>Team."

    mail.send(msg)


@mod.route('/forgot-password', methods=['GET', 'POST'])
def forgot():
    if 'user_id' in session:
        return redirect(url_for('users.home'))

    form = ForgotForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                return user

    # make sure data are valid, but doesn't validate password is right
    return render_template("users/forgot.html", form=form)


@mod.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login form
    """
    if 'user_id' in session:
        return redirect(url_for('users.home'))

    form = LoginForm(request.form)

    # make sure data are valid, but doesn't validate password is right
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            # we use werzeug to validate user's password
            if user and check_password_hash(user.password, form.password.data):
                # the session can't be modified as it's signed,
                # it's a safe place to store the user id
                authorize(user)
                flash('Welcome %s' % user.name)
                return redirect(url_for('users.home'))
        flash('Wrong email or password', 'error-message')

    return render_template('users/login.html', form=form)

@mod.route('/logout', methods=['GET'])
def logout():
    """ Logout action.  """
    if 'user_id' in session:
        del session['user_id']
        g.user = None

    if 'user_id' in session:
        del session['user_id']

    response = make_response(redirect(url_for('users.login')))
    response.set_cookie('sc', '', expires=0)
    return response


@mod.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration Form
    """
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        # create an user instance not yet stored in the database
        # check if email exists
        try:
            exists = db.session.query(User).filter(
                User.email == form.email.data).first()

            if exists:
                flash(
                    'User with this e-mail was registered already.'
                    ' If you forgot your password click ' +
                    '<a href="%s">remind password</a>' % url_for(
                        'users.forgot')
                )
                # redirect user to the 'home' method of the user module.
                return redirect(url_for('users.register'))
        except Exception as e:
            current_app.logger.exception(e)

        alias = ''.join(e for e in form.name.data if e.isalnum())
        try:
            alias_exists = db.session.query(User).filter(
                User.alias == alias).one()
        except Exception as e:
            current_app.logger.exception(e)
            alias_exists = None

        if alias_exists:
            alias = md5.new(form.email.data).hexdigest()

        user = User(
            name=form.name.data,
            email=form.email.data,
            alias=alias,
            password=generate_password_hash(form.password.data)
        )
        # Insert the record in our database and commit it
        db.session.add(user)
        db.session.flush()

        # Log the user in, as he now has an id
        authorize(user)

        try:
            os.mkdir(os.path.join(UPLOAD_FOLDER, str(user.id)), 0775)
        except OSError as e:
            current_app.logger.exception(e)

        db.session.commit()

        # flash will display a message to the user
        flash('Thanks for registering')
        # redirect user to the 'home' method of the user module.
        return redirect(url_for('users.home'))

    return render_template('users/register.html', form=form)


@mod.route("/profile", methods=['GET', 'POST'])
@login_required
@templated('users/profile.html')
def profile():
    user = g.user
    form = ProfileForm(request.form, obj=user)

    if form.validate_on_submit():
        user.name = form.name.data
        user.mobile = form.mobile.data
        user.website = form.website.data
        user.description = form.description.data

        if 'photo' in request.files:
            # remove user photo and thumbs
            mfile = request.files['photo']

            if mfile and allowed_image_file(mfile.filename):

                # if file reuploaded
                if user.photo and len(user.photo) > 0:
                    photo = os.path.join(
                        UPLOAD_FOLDER, str(user.id), user.photo
                    )
                    try:
                        os.remove(photo)
                    except Exception as e:
                        print ("removing %s" % photo)
                        current_app.logger.exception(e)

                    fufile = str(photo.split('.')[0])

                    for basewidth in [200, 245]:
                        thumb = fufile + '_thumb%s.png' % basewidth
                        try:
                            os.remove(thumb)
                        except Exception as e:
                            print ("removing %s" % thumb)
                            current_app.logger.exception(e)

                    user.photo = ''

                filename = secure_filename(mfile.filename)
                ext = filename.rsplit('.', 1)[1]
                fname = '%s_%s' % (g.user.id, g.user.email)
                newfn = '%s.%s' % (base64.b64encode(fname), ext)
                photo = os.path.join(
                    UPLOAD_FOLDER, str(user.id), newfn
                )

                mfile.save(photo)
                user.photo = newfn

        db.session.commit()
        flash("Profile updated")

        # wait until photo will be converted, temporary hack
        time.sleep(1)
        return redirect(url_for("users.profile"))

    return dict(form=form, user=user)


@mod.route("/profile/change-password", methods=['GET', 'POST'])
@login_required
@templated('users/change-password.html')
def change_password():
    user = User.query.get(session['user_id'])
    form = ProfileForm(request.form, obj=user)

    if form.validate_on_submit():
        user.name = form.name.data
        user.country = form.country.data
        user.address = form.address.data
        user.mobile = form.mobile.data
        user.website = form.website.data
        db.session.commit()
        flash("Profile updated")
        return redirect(url_for("users.home"))

    return dict(form=form, user=user)

# vim: set ts=4 sw=4 tw=79 :
