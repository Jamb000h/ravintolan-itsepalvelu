from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv
import sys

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

# Initialize by adding an admin user
sql = "SELECT id FROM users"
result = db.session.execute(sql)
user = result.fetchone()

if user is None:
    hash_value = generate_password_hash('admin')
    sql = "INSERT INTO users (username,password,userType) VALUES ('admin',:password,'admin')"
    db.session.execute(sql, {"password":hash_value})
    db.session.commit()

# Routes

@app.route("/")
def index():
    if session.get("username") is not None:
        if session.get("userType") == "table":
            return redirect("/table")
        if session.get("userType") == "waiter":
            return redirect("/waiter")
        if session.get("userType") == "admin":
            return render_template("index.html")
        return render_template("index.html")
    return render_template("login.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    sql = "SELECT id, userType, password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user != None:
        hash_value = user[2]
        if check_password_hash(hash_value,password):
            session["username"] = username
            session["userId"] = user[0]
            session["userType"] = user[1]
    return redirect("/")

@app.route("/logout")
def logout():
    if session.get("username") is not None:
        del session["username"]
    if session.get("userType") is not None:
        del session["userType"]
    if session.get("userId") is not None:
        del session["userId"]
    return redirect("/")

@app.route("/users", methods=["GET", "POST"])
def users():
    # Admin-only route
    if session.get("userType") != "admin":
        return redirect("/")

    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            userType = request.form["userType"]

            # Check that the username is not reserved and inform user if reserved
            sql = "SELECT id FROM users WHERE username=:username"
            result = db.session.execute(sql, {"username":username})
            user = result.fetchone()

            if user is not None:
                return redirect("/users?duplicateNameError")

            hash_value = generate_password_hash(password)
            sql = "INSERT INTO users (username,password,userType) VALUES (:username,:password,:userType)"
            db.session.execute(sql, {"username":username,"password":hash_value,"userType":userType})
            db.session.commit()
            return redirect("/users")
        except:
            pass

    # Get waiters
    result = db.session.execute("SELECT id, username, userType FROM users WHERE userType = 'waiter'")
    waiters = result.fetchall()

    # Get table users
    result = db.session.execute("SELECT id, username, userType FROM users WHERE userType = 'table'")
    tableusers = result.fetchall()

    # Get admins
    result = db.session.execute("SELECT id, username, userType FROM users WHERE userType = 'admin'")
    admins = result.fetchall()

    return render_template("users.html", waiters=waiters, tableusers=tableusers, admins=admins)

@app.route("/users/<id>", methods=["GET", "POST"])
def editUser(id):
    # Admin-only route
    if session.get("userType") != "admin":
        return redirect("/")

    if request.method == "POST":
        username = request.form["username"]

        # Check that the username is not reserved and inform user if reserved
        sql = "SELECT id FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()

        if user is not None:
            return redirect("/users/"+id+"?duplicateNameError")

        try:
            sql = "UPDATE users SET username=:username WHERE id = :id"
            db.session.execute(sql, {"username": username,"id":id})
            db.session.commit()
            return redirect("/users/"+id)
        except:
            pass

    sql = "SELECT id, username FROM users WHERE id = :id"
    result = db.session.execute(sql, {"id": id})
    user = result.fetchone()
    if user is None:
        return redirect("/users")
    return render_template("editUser.html", user=user)

@app.route("/menu", methods=["GET", "POST"])
def menu():
    # Admin-only route
    if session.get("userType") != "admin":
        return redirect("/")

    if request.method == "POST":
        try:
            itemName = request.form["itemName"]
            itemPrice = request.form["itemPrice"]
            itemCategory = request.form["itemCategory"]
            itemDescription = request.form["itemDescription"]

            # Check that the item name is not reserved and inform user if reserved
            sql = "SELECT id FROM menuItems WHERE itemName=:itemName"
            result = db.session.execute(sql, {"itemName":itemName})
            menuItem = result.fetchone()

            if menuItem is not None:
                return redirect("/menu?duplicateNameError")

            sql = "INSERT INTO menuItems (itemName,itemPrice,itemCategory,itemDescription) VALUES (:itemName,:itemPrice,:itemCategory,:itemDescription)"
            db.session.execute(sql, {"itemName":itemName,"itemPrice":itemPrice,"itemCategory":itemCategory,"itemDescription":itemDescription})
            db.session.commit()
            return redirect("/menu")
        except:
            pass

    sql = "SELECT id, itemName, itemPrice, itemDescription, itemCategory FROM menuItems"
    result = db.session.execute(sql)
    menuItems = result.fetchall() 
    return render_template("menu.html", menuItems=menuItems)

@app.route("/menu/<id>", methods=["GET", "POST"])
def editMenuItem(id):
    # Admin-only route
    if session.get("userType") != "admin":
        return redirect("/")

    if request.method == "POST":
        try:
            itemName = request.form["itemName"]
            itemPrice = request.form["itemPrice"]
            itemCategory = request.form["itemCategory"]
            itemDescription = request.form["itemDescription"]

            # Check that the item name is not reserved and inform user if reserved
            sql = "SELECT id FROM menuItems WHERE itemName=:itemName"
            result = db.session.execute(sql, {"itemName":itemName})
            menuItem = result.fetchone()

            if menuItem is not None:
                return redirect("/menu/"+id+"?duplicateNameError")

            sql = "UPDATE menuItems SET itemName=:itemName, itemPrice=:itemPrice, itemCategory=:itemCategory, itemDescription=:itemDescription WHERE id = :id"
            db.session.execute(sql, {"itemName":itemName, "itemPrice":itemPrice, "itemCategory":itemCategory, "itemDescription":itemDescription,"id":id})
            db.session.commit()
            return redirect("/menu/"+id)
        except:
            pass

    sql = "SELECT id, itemName, itemPrice, itemCategory, itemDescription FROM menuItems WHERE id = :id"
    result = db.session.execute(sql, {"id": id})
    menuItem = result.fetchone()
    if menuItem is None:
        return redirect("/menu")
    return render_template("editMenuItem.html", menuItem=menuItem)

@app.route("/tables", methods=["GET", "POST"])
def tables():
    # Admin-only route
    if session.get("userType") != "admin":
        return redirect("/")

    if request.method == "POST":
        try:
            tableName = request.form["tableName"]
            tableWaiter = request.form["tableWaiter"]
            tableUser = request.form["tableUser"]

            # Check that the table name is not reserved and inform user if reserved
            sql = "SELECT id FROM tables WHERE tableName=:tableName"
            result = db.session.execute(sql, {"tableName":tableName})
            table = result.fetchone()

            if table is not None:
                return redirect("/tables?duplicateNameError")

            # Check waiter
            sql = "SELECT id FROM users WHERE id = :tableWaiter AND userType = 'waiter'"
            result = db.session.execute(sql, {"tableWaiter":tableWaiter})
            waiter = result.fetchone()

            if waiter is None:
                return redirect("/tables?waiterError")

            # Check table user
            sql = "SELECT id FROM users WHERE id = :tableUser AND userType = 'table'"
            result = db.session.execute(sql, {"tableUser":tableUser})
            tUser = result.fetchone()

            if tUser is None:
                return redirect("/tables?tableUserError")

            # Check that the table user is free or reserved for this table
            sql = "SELECT id FROM tables WHERE userId = :tableUser"
            result = db.session.execute(sql, {"tableUser":tableUser})
            tables = result.fetchall()

            if len(tables) > 0 and tables[0][0] is not id:
                return redirect("/tables?reservedUserError")

            sql = "INSERT INTO tables (tableName,waiterId,userId) VALUES (:tableName,:tableWaiter,:tableUser)"
            db.session.execute(sql, {"tableName":tableName,"tableWaiter":tableWaiter,"tableUser":tableUser})
            db.session.commit()
            return redirect("/tables")
        except:
            pass

    # Get tables
    sql = "SELECT t.id, t.tableName, u.username FROM tables t LEFT JOIN users u ON t.waiterId = u.id"
    result = db.session.execute(sql)
    tables = result.fetchall()

    # Get waiters
    sql = "SELECT id, username FROM users WHERE userType = 'waiter'"
    result = db.session.execute(sql)
    waiters = result.fetchall() 

    # Get free table users
    sql = "SELECT id, username FROM users WHERE userType = 'table' AND id NOT IN (SELECT userId FROM tables)"
    result = db.session.execute(sql)
    tableUsers = result.fetchall() 

    return render_template("tables.html", tables=tables, waiters=waiters, tableUsers=tableUsers)

@app.route("/tables/<id>", methods=["GET", "POST"])
def editTable(id):
    # Admin-only route
    if session.get("userType") != "admin":
        return redirect("/logout")

    if request.method == "POST":
        try:
            tableName = request.form["tableName"]
            tableWaiter = request.form["tableWaiter"]
            tableUser = request.form["tableUser"]

            # Check that the table name is not reserved and inform user if reserved
            sql = "SELECT id FROM tables WHERE tableName=:tableName"
            result = db.session.execute(sql, {"tableName":tableName})
            table = result.fetchone()

            if table is not None:
                return redirect("/tables/"+id+"?duplicateNameError")

            # Check waiter
            sql = "SELECT id FROM users WHERE id = :tableWaiter AND userType = 'waiter'"
            result = db.session.execute(sql, {"tableWaiter":tableWaiter})
            waiter = result.fetchone()

            if waiter is None:
                return redirect("/")

            # Check table user
            sql = "SELECT id FROM users WHERE id = :tableUser AND userType = 'table'"
            result = db.session.execute(sql, {"tableUser":tableUser})
            tUser = result.fetchone()

            if tUser is None:
                return redirect("/")

            # Check that the table user is free or reserved for this table
            sql = "SELECT id FROM tables WHERE id = :tableUser"
            result = db.session.execute(sql, {"tableUser":tableUser})
            tables = result.fetchall()

            if len(tables) > 0 and tables[0][0] != id:
                return redirect("/")

            # Update table
            sql = "UPDATE tables SET tableName=:tableName, waiterId=:tableWaiter, userId=:tableUser WHERE id = :id"
            db.session.execute(sql, {"tableName":tableName,"tableWaiter":tableWaiter, "tableUser":tableUser, "id":id})
            db.session.commit()

            return redirect("/tables/"+id)
        except:
            pass

    # Get table
    sql = "SELECT t.id, t.tableName, u.id, t.userId FROM tables t LEFT JOIN users u ON t.waiterId = u.id WHERE t.id=:id"
    result = db.session.execute(sql, {"id":id})
    table = result.fetchone()

    # Get waiters
    sql = "SELECT id, username FROM users WHERE userType = 'waiter'"
    result = db.session.execute(sql)
    waiters = result.fetchall() 

    # Get free table users and the table user reserved for this table
    sql = "SELECT id, username FROM users WHERE userType = 'table' AND id NOT IN (SELECT userId FROM tables WHERE id != :id)"
    result = db.session.execute(sql, {"id":id})
    tableUsers = result.fetchall() 

    return render_template("editTable.html", table=table, waiters=waiters, tableUsers=tableUsers)

@app.route("/order", methods=["GET", "POST"])
def orders():
    # Table-only route
    if session.get("userType") != "table":
        return redirect("/")

    if request.method == "POST":
        tableId = request.form["tableId"]

        # Check that the current user is the user for this table
        sql = "SELECT id FROM tables WHERE userId = :userId"
        result = db.session.execute(sql, {"userId":session.get("userId")})
        tableIdForUser = result.fetchone()[0]

        if int(tableIdForUser) != int(tableId):
            return redirect("/")

        try:
            sql = "INSERT INTO orders (tableId, orderStatus, created_at) VALUES (:tableId, 'new', NOW()) RETURNING id"
            result = db.session.execute(sql, {"tableId":tableId})
            orderId = result.fetchone()[0]

            menuItemIds = request.form.getlist("menuItemId")
            menuItemQuantities = request.form.getlist("menuItemQty")
            for i, menuItemId in enumerate(menuItemIds):
                if menuItemQuantities[i] != "":
                    sql = "INSERT INTO orderItems (orderId, menuItemId, quantity) VALUES (:orderId, :menuItemId, :quantity)"
                    db.session.execute(sql, {"orderId":orderId, "menuItemId":menuItemId, "quantity":menuItemQuantities[i]})
            db.session.commit()
            return redirect("/table")
        except:
            pass

    # Get menu item categories
    sql = "SELECT unnest(enum_range(NULL::menuItemCategory))"
    result = db.session.execute(sql)
    menuItemCategories = result.fetchall()

    # Get menu items
    sql = "SELECT id, itemName, itemPrice, itemDescription, itemCategory FROM menuItems"
    result = db.session.execute(sql)
    menuItems = result.fetchall() 

    # Get table id
    sql = "SELECT id FROM tables WHERE userId = :userId"
    result = db.session.execute(sql, {"userId": session.get("userId")})
    tableId = result.fetchone()[0]
    return render_template("order.html", menuItems=menuItems, tableId=tableId, menuItemCategories=menuItemCategories)

@app.route("/proceedOrder/<id>", methods=["GET"])
def proceedOrder(id):
    # Route only for waiter and admin
    if session.get("userType") == "table":
        return redirect("/")

    # Get order
    sql = "SELECT id, orderStatus FROM orders WHERE id=:id"
    result = db.session.execute(sql, "id":id})
    order = result.fetchone()

    if order is None:
        return redirect("/")

    currentStatus = order[1]
    # Get new status. Can proceed only until completed.
    newStatus = getNewStatus(currentStatus)

    if newStatus != currentStatus:
        try:
            sql = "UPDATE orders SET orderStatus=:orderStatus WHERE id = :id"
            db.session.execute(sql, {"orderStatus":newStatus,"id":id})
            db.session.commit()
        except:
            pass
    
    return redirect("/")

@app.route("/cancelOrder/<id>", methods=["GET"])
def cancelOrder(id):
    # Get order
    sql = "SELECT o.id, o.tableId, u.id, t.userId, o.orderStatus FROM orders o LEFT JOIN tables t ON o.tableId = t.id AND o.id = :id"
    result = db.session.execute(sql, {"id":id})
    order = result.fetchone()

    if order is None:
        return redirect("/")

    if session.get("userType") == "table":
        # Check that the user is correct
        tableUserId = order[3]

        if int(tableUserId) != int(session.get("userId")):
            return redirect("/")

    # Only orders with status "new" can be cancelled
    if order[4] == "new":
        try:
            sql = "UPDATE orders SET orderStatus='cancelled' WHERE id = :id"
            db.session.execute(sql, {"id":id})
            db.session.commit()
        except:
            pass
    
    return redirect("/order/"+id)


@app.route("/table", methods=["GET"])
def table():
    # Table-only route
    if session.get("userType") != "table":
        return redirect("/")

    # Get table and waiter information for user
    sql = "SELECT t.id, t.tableName, u.username FROM tables t LEFT JOIN users u ON t.waiterId = u.id WHERE t.userId=:id"
    result = db.session.execute(sql, {"id":session.get("userId")})
    table = result.fetchone()

    if table is None:
        return redirect("/notable")

    # Get waiter name    
    waiterName = table[2]

    # Get orders for table
    sql = "SELECT id, orderStatus, created_at FROM orders WHERE tableId = :tableId AND orderStatus != 'paid' ORDER BY id"
    result = db.session.execute(sql, {"tableId":table[0]})
    orders = result.fetchall()

    # Get order items for table
    sql = "SELECT o.orderId, o.quantity, m.itemName, m.itemPrice, m.itemDescription FROM menuItems m LEFT JOIN orderItems o ON o.menuItemId = m.id LEFT JOIN orders os ON o.orderId = os.id WHERE os.tableId = :tableId"
    result = db.session.execute(sql, {"tableId":table[0]})
    orderItems = result.fetchall()

    # Calculate order totals
    sql = "SELECT o.orderId, SUM(o.quantity * m.itemPrice) FROM orderItems o LEFT JOIN menuItems m ON m.id = o.menuItemId LEFT JOIN orders os ON o.orderId = os.id WHERE os.tableId = :tableId GROUP BY o.orderId ORDER BY o.orderId"
    result = db.session.execute(sql, {"tableId":table[0]})
    orderTotals = result.fetchall()


    # Calculate grand total
    grandTotal = 0
    for orderItem in orderItems:
        grandTotal += orderItem[1] * orderItem[3]

    return render_template("table.html", table=table, waiterName=waiterName, orders=orders, orderItems=orderItems, orderTotals=orderTotals, grandTotal=grandTotal)


@app.route("/waiter", methods=["GET"])
def table():
    # Waiter-only route
    if session.get("userType") != "waiter":
        return redirect("/")

    # Get table and waiter information for user
    sql = "SELECT t.id, t.tableName, u.username FROM tables t LEFT JOIN users u ON t.waiterId = u.id WHERE t.userId=:id"
    result = db.session.execute(sql, {"id":session.get("userId")})
    table = result.fetchone()

    if table is None:
        return redirect("/notable")

    # Get waiter name    
    waiterName = table[2]

    # Get orders for table
    sql = "SELECT id, orderStatus, created_at FROM orders WHERE tableId = :tableId AND orderStatus != 'paid' ORDER BY id"
    result = db.session.execute(sql, {"tableId":table[0]})
    orders = result.fetchall()

    # Get order items for table
    sql = "SELECT o.orderId, o.quantity, m.itemName, m.itemPrice, m.itemDescription FROM menuItems m LEFT JOIN orderItems o ON o.menuItemId = m.id LEFT JOIN orders os ON o.orderId = os.id WHERE os.tableId = :tableId"
    result = db.session.execute(sql, {"tableId":table[0]})
    orderItems = result.fetchall()

    # Calculate order totals
    sql = "SELECT o.orderId, SUM(o.quantity * m.itemPrice) FROM orderItems o LEFT JOIN menuItems m ON m.id = o.menuItemId LEFT JOIN orders os ON o.orderId = os.id WHERE os.tableId = :tableId GROUP BY o.orderId ORDER BY o.orderId"
    result = db.session.execute(sql, {"tableId":table[0]})
    orderTotals = result.fetchall()


    # Calculate grand total
    grandTotal = 0
    for orderItem in orderItems:
        grandTotal += orderItem[1] * orderItem[3]

    return render_template("table.html", table=table, waiterName=waiterName, orders=orders, orderItems=orderItems, orderTotals=orderTotals, grandTotal=grandTotal)

@app.route("/notable", methods=["GET"])
def notable():
    return render_template("notable.html")

def getNewStatus(oldStatus):
    if(oldStatus == "new"):
        return "inprogress"

    if(oldStatus == "inprogress"):
        return "completed"

    return oldStatus