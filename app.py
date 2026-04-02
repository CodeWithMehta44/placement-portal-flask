from flask import Flask
from models import db
from models import *

app = Flask(__name__)

# load config file
app.config.from_pyfile('config.py')

db.init_app(app)

#create database 
with app.app_context(): #needed to access DB in flask
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)