from flask import Flask, Response
from prometheus_flask_exporter import PrometheusMetrics
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy

import os
import sys
import random
import platform
from config import Config

animal = Config.ANIMAL
hostname = platform.node()

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
metrics = PrometheusMetrics(app)
print(app.config)
db = SQLAlchemy(app)

class Type(db.Model):
  __tablename__ = 'types'

  id = db.Column(db.Integer, primary_key=True)
  type = db.Column(db.String())

  def __init__(self, type):
    self.type = type

  def __repr__(self):
    return f"{self.type}"

class Name(db.Model):
  __tablename__ = 'names'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String())

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return f"{self.name}"

def populate_types():
  for t in ["cat", "dog"]:
    exists = Type.query.filter_by(type=t).first()
    if not exists:
      a = Type(type=t)
      db.session.add(a)

def populate_names():
  for n in list(open("data/names")):
    n = n.rstrip()
    exists = Name.query.filter_by(name=n).first()
    if not exists:
      a = Name(name=n)
      db.session.add(a)

@app.route('/readyz')
@metrics.do_not_track()
def readyz():
  if animal:
    try:
      exists = Type.query.filter_by(type=animal).first()
    except sqlalchemy.exc.DatabaseError:
      db.create_all()
    except Exception as e:
      return Response(f"Database error: {e}", mimetype='text/plain',status=500)
    if exists:
      return Response("ok", mimetype='text/plain',status=200)
  else:
    return Response(f"missing type", mimetype='text/plain',status=500)
  return Response(f"unknown type {animal}", mimetype='text/plain',status=500)

@app.route('/livez')
@metrics.do_not_track()
def livez():
    return Response('ok', mimetype='text/plain',status=200)

@app.route('/')
def catdog():
    body = ''
    status = 500
    try:
      names = list(Name.query.all())
    except sqlalchemy.exc.DatabaseError:
      db.create_all()
      return Response(f"There is no {animal} living on {hostname}.", mimetype='text/plain', status=200)
    except sqlalchemy.exc.DisconnectionError:
      return Response(f"Database disconnected.", mimetype='text/plain', status=500)
    except Exception as e:
      return Response(f"Database error: {e}", mimetype='text/plain', status=500)
    if animal:
      if names:
        name = random.choice(names)
        body = f"It's a {animal} named {name} living on {hostname}."
      else:
        body = f"There is no {animal} living on {hostname}."
      status = 200
    else:
      body = f"It's something weird on {hostname}."
      status = 500
    return Response(body, mimetype='text/plain', status=status)

@app.route('/version')
def version():
    return Response(f"{Config.VERSION}", mimetype='text/plain', status=200)
  

if __name__ == "__main__":
  with app.test_request_context():
    try:
      db.create_all()
    except sqlalchemy.exc.OperationalError as e:
      print(f"Can't connect to database.")
      sys.exit(-1)
    except Exception as e:
      print(f"Database error: {e}")
      sys.exit(-2)
    populate_names()
    populate_types()
    db.session.commit()
  app.run(port=Config.PORT, host=Config.HOST)
