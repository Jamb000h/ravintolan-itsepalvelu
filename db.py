from app import app
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import generate_password_hash

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")

db = SQLAlchemy(app)

# Initialize by adding default users if no users present
sql = "SELECT id FROM users"
result = db.session.execute(sql)
user = result.fetchone()

if user is None:
    try:
        hash_value = generate_password_hash('admin1')
        sql = "INSERT INTO users (username,password,userType) VALUES ('admin1',:password,'admin')"
        db.session.execute(sql, {"password": hash_value})

        hash_value = generate_password_hash('waiter1')
        sql = "INSERT INTO users (username,password,userType) VALUES ('waiter1',:password,'waiter')"
        db.session.execute(sql, {"password": hash_value})

        hash_value = generate_password_hash('table1')
        sql = "INSERT INTO users (username,password,userType) VALUES ('table1',:password,'table')"
        db.session.execute(sql, {"password": hash_value})

        db.session.commit()
    except:
        pass
