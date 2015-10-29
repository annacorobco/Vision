#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask.ext.admin import Admin
from flask.ext import admin, login
from flask.ext.babel import Babel
from flask.ext.blogging import SQLAStorage, BloggingEngine
from sqlalchemy import create_engine, MetaData

app = Flask(__name__, static_url_path='/app/static')
app.config.from_object('config')
db = SQLAlchemy(app)

# blogging
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
meta = MetaData()
sql_storage = SQLAStorage(engine, metadata=meta)
blog = BloggingEngine(app, sql_storage)
meta.create_all(bind=engine)

db.create_all()
mail = Mail(app)
babel = Babel(app)

from app.admin.views import MyAdminIndexView

backend = Admin(
    app,
    app.config['APP_NAME'],
    index_view=MyAdminIndexView(),
    base_template='admin.html'
)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def error_500(error):
    return render_template('500.html'), 500

# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    @blog.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)

# Initialize flask-login
init_login()


from app.users.models import User, Role
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from app.home.views import mod as homeModule
app.register_blueprint(homeModule)

from app.users.views import mod as userModule
app.register_blueprint(userModule)

from app.admin.views import UserAdmin, RoleAdmin
backend.add_view(UserAdmin(db.session))
backend.add_view(RoleAdmin(db.session))
