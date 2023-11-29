from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash
from os import path

# Define a base class for SQLAlchemy models using declarative_base
Base = declarative_base()

# Initialize SQLAlchemy with the custom base class
db = SQLAlchemy(model_class=Base)

# Define the name of the SQLite database file
DATABASE = "GXOBackhaulDB.db"


# Function to create the Flask application
def create_app():
    app = Flask(__name__)

    # Flask application configuration settings
    app.config['SECRET_KEY'] = 'HJ7Hgr5thm5saWASE547vfds'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE}'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize and attach SQLAlchemy to the app
    db.init_app(app)

    # Import and register blueprints for different parts of the app
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import User and Admin models and create an admin user if not exists
    from .models import User

    def create_admin():
        users = User.query.filter_by().count()
        if users == 0:
            email = "admin@admin.com"
            password = "AdminPassword123!"
            is_admin = True
            first_name = "GXO"
            last_name = "Admin"
            phone = ""
            admin = User(email=email,
                         password=generate_password_hash(
                             password, method='pbkdf2:sha1', salt_length=8),
                         is_admin=is_admin,
                         first_name=first_name,
                         last_name=last_name,
                         phone=phone)
            db.session.add(admin)
            db.session.commit()
        else:
            pass

    # Create all database tables and create admin user during app context
    with app.app_context():
        db.create_all()
        create_admin()

    # Initialize Flask-Login and configure user loader
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        user = User.query.get(int(id))
        return user

    return app


# Function to create the database if it doesn't exist
def create_database(app):
    if not path.exists('website/' + DATABASE):
        db.create_all(app=app)
        print('Created Database!')
