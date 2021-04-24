from app import app
from flask import render_template, request, redirect, session
import users, menu, tables, orders

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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    if users.login(username, password):
        return redirect("/")

    return redirect("/login")


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")


@app.route("/users", methods=["GET", "POST"])
def listUsers():
    # Admin-only route
    if session.get("userType") != "admin":
        return redirect("/")

    if request.method == "POST":
        if session["csrfToken"] != request.form["csrfToken"]:
            abort(403)

        username = request.form["username"]
        password = request.form["password"]
        userType = request.form["userType"]

        users.register(username, password, userType)
        return redirect("/users")

    return render_template("users.html",
                           waiters=users.getUsersByUserType("waiter"),
                           tableusers=users.getUsersByUserType("table"),
                           admins=users.getUsersByUserType("admin"))


@app.route("/users/<id>", methods=["GET", "POST"])
def editUser(id):
    # Admin-only route
    if session.get("userType") != "admin":
        return redirect("/")

    if request.method == "POST":
        if session["csrfToken"] != request.form["csrfToken"]:
            abort(403)

        username = request.form["username"]
        password = request.form["password"]

        users.editUser(id, username, password)
        return redirect("/users/"+id)

    user = users.getUserById(id)

    if user is None:
        return redirect("/users")

    return render_template("editUser.html", user=user)


@app.route("/menu", methods=["GET", "POST"])
def listMenu():
    # Admin-only route
    if session.get("userType") != "admin":
        return redirect("/")

    if request.method == "POST":
        if session["csrfToken"] != request.form["csrfToken"]:
            abort(403)

        itemName = request.form["itemName"]
        itemPrice = request.form["itemPrice"]
        itemCategory = request.form["itemCategory"]
        itemDescription = request.form["itemDescription"]

        menu.addMenuItem(itemName, itemPrice, itemCategory, itemDescription)

        return redirect("/menu")

    return render_template("menu.html", menuItems=menu.getMenu())


@app.route("/menu/<id>", methods=["GET", "POST"])
def editMenuItem(id):
    # Admin-only route
    if session.get("userType") != "admin":
        return redirect("/")

    if request.method == "POST":
        if session["csrfToken"] != request.form["csrfToken"]:
            abort(403)

        itemName = request.form["itemName"]
        itemPrice = request.form["itemPrice"]
        itemCategory = request.form["itemCategory"]
        itemDescription = request.form["itemDescription"]

        menu.editMenuItem(id, itemName, itemPrice,
                          itemCategory, itemDescription)

        return redirect("/menu/"+id)

    menuItem = menu.getMenuItemById(id)

    if menuItem is None:
        return redirect("/menu")

    return render_template("editMenuItem.html", menuItem=menuItem)


@app.route("/tables", methods=["GET", "POST"])
def listTables():
    # Admin-only route
    if session.get("userType") != "admin":
        return redirect("/")

    if request.method == "POST":
        if session["csrfToken"] != request.form["csrfToken"]:
            abort(403)

        tableName = request.form["tableName"]
        tableWaiter = request.form["tableWaiter"]
        tableUser = request.form["tableUser"]

        tables.addTable(tableName, tableWaiter, tableUser)

    return render_template("tables.html",
                           tables=tables.getTablesWithWaiters(),
                           waiters=users.getUsersByUserType("waiter"),
                           tableUsers=users.getFreeTableUsers())


@app.route("/tables/<id>", methods=["GET", "POST"])
def editTable(id):
    # Admin-only route
    if session.get("userType") != "admin":
        return redirect("/logout")

    if request.method == "POST":
        if session["csrfToken"] != request.form["csrfToken"]:
            abort(403)

        tableName = request.form["tableName"]
        tableWaiter = request.form["tableWaiter"]
        tableUser = request.form["tableUser"]

        tables.editTable(id, tableName, tableWaiter, tableUser)

        return redirect("/tables/"+id)

    return render_template("editTable.html",
                           table=tables.getTableAndWaiterByTableId(id),
                           waiters=users.getUsersByUserType("waiter"),
                           tableUsers=users.getTableUsersForTable(id))


@app.route("/order", methods=["GET", "POST"])
def listOrders():
    # Table-only route
    if session.get("userType") != "table":
        return redirect("/")

    if request.method == "POST":
        if session["csrfToken"] != request.form["csrfToken"]:
            abort(403)

        tableId = request.form["tableId"]
        menuItemIds = request.form.getlist("menuItemId")
        menuItemQuantities = request.form.getlist("menuItemQty")

        orders.order(tableId, menuItemIds, menuItemQuantities)
        return redirect("/table")

    return render_template("order.html",
                           menuItems=menu.getMenu(),
                           tableId=tables.getTableIdForUser(),
                           menuItemCategories=menu.getMenuItemCategories())


@app.route("/proceedorder/<id>", methods=["GET"])
def proceedOrder(id):
    # Route only for waiter and admin
    if session.get("userType") == "table":
        return redirect("/")

    order = orders.getOrderById(id)

    if not order:
        return redirect("/")

    currentStatus = order[1]
    newStatus = orders.getNewStatus(currentStatus)

    if newStatus != currentStatus:
        orders.updateOrderStatus(id, newStatus)

    return redirect("/")


@app.route("/cancelorder/<id>", methods=["GET"])
def cancelOrder(id):
    # Get order
    order = orders.getTableIdAndStatusForOrder(id)

    if not order:
        return redirect("/")

    if session.get("userType") == "table":
        # Check that the user is correct
        tableUserId = order[0]

        if int(tableUserId) != int(session.get("userId")):
            return redirect("/")

    # Only orders with status "new" can be cancelled
    if order[1] == "new":
        orders.updateOrderStatus(id, "cancelled")

    return redirect("/")


@app.route("/table", methods=["GET"])
def table():
    # Table-only route
    if session.get("userType") != "table":
        return redirect("/")

    # Get table and waiter information for user
    table = tables.getTableAndWaiterForUser()

    if not table:
        return redirect("/notable")

    tableOrders = orders.getOrdersForTable(table[0])
    orderItems = orders.getOrderItemsForTable(table[0])
    totals = orders.calculateOrderTotals(orderItems)

    return render_template("table.html",
                           table=table,
                           waiterName=table[2],
                           orders=tableOrders,
                           orderItems=orderItems,
                           grandTotal=totals["grandTotal"],
                           orderTotals=totals["orderTotals"],
                           hasOrdersToPay=orders.hasOrdersToPay(table[0]))


@app.route("/waiter", methods=["GET"])
def waiter():
    # Waiter-only route
    if session.get("userType") != "waiter":
        return redirect("/")

    waiterTables = tables.getTablesForWaiter()
    waiterOrders = orders.getOrdersForWaiter()
    orderItems = orders.getOrderItemsForWaiter()
    orderTotals = orders.calculateOrderTotals(orderItems)["orderTotals"]

    return render_template("waiter.html",
                           tables=waiterTables,
                           orders=waiterOrders,
                           orderItems=orderItems,
                           orderTotals=orderTotals)

@app.route("/wantstopay/<id>", methods=["GET"])
def wantstopay(id):
    # Table-only route
    if session.get("userType") != "table":
        return redirect("/")

    # Check that user owns the table
    tableId = tables.getTableIdForUser()

    if tableId is None or (int(tableId) != int(id)):
        return redirect("/")

    if not orders.hasOrdersToPay(id):
        return redirect("/")

    orders.cancelNewOrdersForTable(id)
    tables.setWantsToPay(id, True)

    return redirect("/table")

@app.route("/haspaid/<id>", methods=["GET"])
def haspaid(id):
    # Waiter and admin only
    if session.get("userType") == "table":
        return redirect("/")

    if orders.hasOrdersInProgress(id):
        return redirect("/")

    orders.markOrdersForTableAsPaid(id)
    tables.setWantsToPay(id, False)

    return redirect("/table")

@app.route("/notable", methods=["GET"])
def notable():
    return render_template("notable.html")
