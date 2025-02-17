from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy import text

app = Flask(__name__)

# Ganti dengan database yang ingin dibuat
DATABASE_NAME = "article"
DATABASE_URI = f"mysql+pymysql://root:@localhost/{DATABASE_NAME}"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

def create_database():
  engine = sqlalchemy.create_engine(DATABASE_URI.rsplit("/", 1)[0])
  conn = engine.connect()
  conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))
  conn.close()

if __name__ == "__main__":
  create_database()
  print(f"Database '{DATABASE_NAME}' berhasil dibuat!")
