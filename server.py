from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase
import os
import string

alphabets = list(string.ascii_letters)
digits = [0,1,2,3,4,5,6,7,8,9]
hashable_list = alphabets + digits

class Base(DeclarativeBase):
  pass
# encode takes a long form url and manipulates 
# BUG: currently utilizes len of database instead of long_url's id. this is incorrect. We must create the unique short with long_urls id placement
def encode():
   ret_str = "http://127.0.0.1:5000/go/"
   digits = []
   encoder_offset = next_id() + 1
   print(encoder_offset)
   num = encoder_offset
   while num > 0:
    remainder = int(num % 62)
    digits.append(remainder)
    num = int(num / 62)

   digits.reverse()
   for dig in digits:
      ret_str += hashable_list[dig]
   return ret_str


def decode(url):
   pwr = len(url)
   id = 0
   for ch in url:
      id += hashable_list.index(ch) * pow(62,pwr-1)
   return id 

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)

# Connection setup, utilizing personal postgresql db
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['CONNECTION_STRING']
db = SQLAlchemy(app)

def next_id():
   ids = db.session.execute(db.select(UrlData).order_by(UrlData.id)).scalars()
   return (len(ids.fetchall()))


# Schema for table I will be using to manage user data
class UrlData(db.Model):
   __tablename__ = 'url_table'
   id = db.Column(db.Integer, primary_key=True)
   long_url = db.Column(db.String)
   short_url = db.Column(db.String, nullable=True)

   def __init__(self,long_url, short_url) -> None:
      super(UrlData).__init__()
      self.long_url = long_url
      self.short_url = short_url

# db creation
with app.app_context():
   db.create_all()

@app.route("/")
def main_page():
    # Fetch recent shortend endpoints to display for the users quick access
    return render_template("hompage.jinja2")


@app.route("/url/generate", methods=["GET","POST"])
# NOTE: Before posting to the database, check if the long url is already present, if so just return the short url that should accompany it.
def add_url_data():
   if request.method == "POST":
        if(request.form.get("long_url")):
           long_url_data = request.form.get("long_url")
           encoded = encode()
           data = UrlData(
              long_url=long_url_data,
              short_url=encoded
           )
           db.session.add(data)
           db.session.commit()
        else:
           return render_template('error.jinja2')
        return render_template('hompage.jinja2')

# /go/: will recieve shortened urls that will decode and redirect user to the specified endpoint
@app.route("/go/<code>", methods=["GET"])
def url_redirect(code):
   data = decode(code)
   result = db.session.execute(db.select(UrlData).where(UrlData.id == data)).scalar()

   
   return redirect(result.__dict__["long_url"])