from db import db
from flask import flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from os import urandom

def login(username, password):
    user = getUserByUsername(username)
    if user is None:
        return False

    hash_value = user[2]
    
    if check_password_hash(hash_value, password):
        session["username"] = username
        session["userId"] = user[0]
        session["userType"] = user[1]
        session["csrfToken"] = urandom(16).hex()

        return True

    return False


def logout():
    if session.get("username") is not None:
        del session["username"]
    if session.get("userType") is not None:
        del session["userType"]
    if session.get("userId") is not None:
        del session["userId"]
    if session.get("csrfToken") is not None:
        del session["csrfToken"]


def register(username, password, userType):
    if usernameIsReserved(username):
        return

    try:
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (username,password,userType) VALUES (:username,:password,:userType)"
        db.session.execute(
            sql, {"username": username, "password": hash_value, "userType": userType})
        db.session.commit()
    except:
        pass


def editUser(id, username, password):
    if usernameIsReserved(username) and int(getUserByUsername(username)[0]) != int(id):
        return

    try:
        hash_value = generate_password_hash(password)
        sql = "UPDATE users SET username=:username, password=:password WHERE id = :id"
        db.session.execute(
            sql, {"username": username, "password": hash_value, "id": id})
        db.session.commit()
    except:
        pass


def getUsersByUserType(userType):
    sql = "SELECT id, username, userType FROM users WHERE userType = :userType"
    result = db.session.execute(sql, {"userType": userType})
    return result.fetchall()


def getUserByUsername(username):
    sql = "SELECT id, userType, password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    return result.fetchone()


def usernameIsReserved(username):
    user = getUserByUsername(username)

    if user is not None:
        return True

    return False


def getUserById(id):
    sql = "SELECT id, username FROM users WHERE id = :id"
    result = db.session.execute(sql, {"id": id})
    return result.fetchone()


def getUserByTypeAndId(userType, id):
    sql = "SELECT id FROM users WHERE id = :id AND userType = :userType"
    result = db.session.execute(sql, {"userType": userType, "id": id})
    return result.fetchone()


def getFreeTableUsers():
    sql = "SELECT id, username FROM users WHERE userType = 'table' AND id NOT IN (SELECT userId FROM tables)"
    result = db.session.execute(sql)
    return result.fetchall()


def getTableUsersForTable(id):
    sql = "SELECT id, username FROM users WHERE userType = 'table' AND id NOT IN (SELECT userId FROM tables WHERE id != :id)"
    result = db.session.execute(sql, {"id": id})
    return result.fetchall()

def validCredentials(username, password):
    if len(username) < 6 or len(password) < 6:
        flash("Username or password too short! Minimum length is 5 characters.")
        return False
    return True