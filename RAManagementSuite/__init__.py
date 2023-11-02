import os
from flask import Flask
from RAManagementSuite import models
from .extensions import db, migrate
from .models import Announcement

# from .models import User

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


# def initialize_database():
#     import sqlite3
#
#     connection = sqlite3.connect(DB_PATH)
#
#     with open('schema.sql') as f:
#         connection.executescript(f.read())
#
#     cur = connection.cursor()
#     cur.execute("INSERT INTO announcements (title, content) VALUES (?, ?)",
#                 ('First Announcement', 'Content for the first announcement')
#                 )
#     cur.execute("INSERT INTO announcements (title, content) VALUES (?, ?)",
#                 ('Second Announcement', 'Content for the second announcement')
#                 )
#
#     connection.commit()
#     connection.close()

def initialize_database():
    # Check if the table is empty
    if not Announcement.query.first():
        initial_announcements = [
            Announcement(title='First Announcement', content='Content for the first announcement'),
            Announcement(title='Second Announcement', content='Content for the second announcement')
        ]
        for ann in initial_announcements:
            db.session.add(ann)
        db.session.commit()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH

    db.init_app(app)
    migrate.init_app(app, db)  # for quickly changing the db

    from RAManagementSuite.views.auth import auth
    app.register_blueprint(auth)

    from RAManagementSuite.views.home import home
    app.register_blueprint(home)

    with app.app_context():
        db.create_all()  # this creates all tables based on the models defined
        initialize_database()  # this will populate the database based on schema.sql and add initial data

    return app
