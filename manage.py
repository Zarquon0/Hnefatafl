from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os

#Initialize app
app = Flask(__name__)

#Configure app
app.config['SECRET_KEY'] = 'development'
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'hnefatafl_storage.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Initiliaze key objects
lm = LoginManager()
lm.init_app(app)
db = SQLAlchemy(app)

import views, models