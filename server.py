from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['CONNECTION_STRING']
db = SQLAlchemy(app)


class UrlData(db.Model):
   __tablename__ = 'url_table'
   id = db.Column(db.Integer, primary_key=True)
   long_url = db.Column(db.String)
   short_url = db.Column(db.String, nullable=True)

   def __init__(self,long_url, short_url) -> None:
      super(UrlData).__init__()
      self.long_url = long_url
      self.short_url = short_url


with app.app_context():
   db.create_all()


@app.route("/")
def hello_world():
    return render_template("hompage.jinja2")

@app.route("/url", methods=["GET","POST"])
def add_url_data():
   if request.method == "POST":
      long_url = request.form.get("long_url")
