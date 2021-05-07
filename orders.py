from db import db
from flask import flash, session

def order(tableId, menuItemIds, menuItemQuantities):
    # Check that the current user is the user for this table
    sql = "SELECT id, wantsToPay FROM tables WHERE userId = :userId"
    result = db.session.execute(sql, {"userId": session.get("userId")})
    table = result.fetchone()

    # If wrong user or table wants to pay, don't allow ordering
    if int(table[0]) != int(tableId) or table[1] == True:
        flash("Wrong user! Please contact your waiter.")
        return

    try:
        sql = "INSERT INTO orders (tableId, orderStatus, created_at) VALUES (:tableId, 'new', NOW()) RETURNING id"
        result = db.session.execute(sql, {"tableId": tableId})
        orderId = result.fetchone()[0]

        for i, menuItemId in enumerate(menuItemIds):
            if menuItemQuantities[i] != "" and int(menuItemQuantities[i]) > 0:
                addItemToOrder(orderId, menuItemId, menuItemQuantities[i])
    except:
        pass

def addItemToOrder(orderId, menuItemId, quantity):
    sql = "INSERT INTO orderItems (orderId, menuItemId, quantity) VALUES (:orderId, :menuItemId, :quantity)"
    db.session.execute(sql, {"orderId": orderId, "menuItemId": menuItemId, "quantity": quantity})
    db.session.commit()

def getOrderById(id):
    sql = "SELECT id, orderStatus FROM orders WHERE id=:id"
    result = db.session.execute(sql, {"id": id})
    return result.fetchone()

def getTableIdAndStatusForOrder(id):
    sql = "SELECT t.userId, o.orderStatus FROM orders o LEFT JOIN tables t ON o.tableId = t.id WHERE o.id = :id"
    result = db.session.execute(sql, {"id": id})
    return result.fetchone()

def updateOrderStatus(id, orderStatus):
    try:
        sql = "UPDATE orders SET orderStatus=:orderStatus, updated_at=NOW() WHERE id = :id"
        db.session.execute(sql, {"orderStatus": orderStatus, "id": id})
        db.session.commit()
    except:
        pass

def getNewStatus(oldStatus):
    if(oldStatus == "new"):
        return "inprogress"

    if(oldStatus == "inprogress"):
        return "completed"

    return oldStatus

def getOrdersForTable(tableId):
    sql = "SELECT id, orderStatus, created_at FROM orders WHERE tableId = :tableId AND orderStatus != 'paid' AND orderStatus != 'cancelled' ORDER BY id"
    result = db.session.execute(sql, {"tableId": tableId})
    return result.fetchall()

def hasOrdersToPay(tableId):
    sql = "SELECT id FROM orders WHERE tableId = :tableId AND orderStatus = 'completed'"
    result = db.session.execute(sql, {"tableId": tableId})
    if len(result.fetchall()) > 0:
        return True
    return False

def hasOrdersInProgress(tableId):
    sql = "SELECT id FROM orders WHERE tableId = :tableId AND orderStatus = 'inprogress'"
    result = db.session.execute(sql, {"tableId": tableId})
    if len(result.fetchall()) > 0:
        return True
    return False

def getOrderItemsForTable(tableId):
    sql = "SELECT o.orderId, o.quantity, m.itemName, m.itemPrice, m.itemDescription FROM menuItems m LEFT JOIN orderItems o ON o.menuItemId = m.id LEFT JOIN orders os ON o.orderId = os.id WHERE os.tableId = :tableId AND os.orderStatus != 'cancelled' AND os.orderStatus != 'paid'"
    result = db.session.execute(sql, {"tableId": tableId})
    return result.fetchall()

def getOrdersForWaiter():
    sql = "SELECT o.id, o.created_at, o.orderStatus, o.tableId, t.tableName, o.updated_at FROM orders o LEFT JOIN tables t ON o.tableId = t.id WHERE t.waiterId = :id AND o.orderStatus != 'paid' AND o.orderStatus != 'cancelled' ORDER BY created_at asc"
    result = db.session.execute(sql, {"id": session.get("userId")})
    return result.fetchall()

def getOrderItemsForWaiter():
    sql = "SELECT oi.orderId, oi.quantity, m.itemName, m.itemPrice FROM menuItems m LEFT JOIN orderItems oi ON m.id = oi.menuItemId LEFT JOIN orders o ON oi.orderId = o.id LEFT JOIN tables t ON o.tableId = t.id WHERE t.waiterId = :id AND o.orderStatus != 'paid' AND o.orderStatus != 'cancelled'"
    result = db.session.execute(sql, {"id": session.get("userId")})
    return result.fetchall()

def cancelNewOrdersForTable(id):
    try:
        sql = "UPDATE orders SET orderStatus = 'cancelled' WHERE tableId = :id AND orderStatus = 'new'"
        db.session.execute(sql, {"id": id})
        db.session.commit()
    except:
        pass

def markOrdersForTableAsPaid(id):
    try:
        sql = "UPDATE orders SET orderStatus = 'paid' WHERE tableId = :id AND orderStatus != 'cancelled' AND orderStatus != 'new'"
        db.session.execute(sql, {"id": id})
        db.session.commit()
    except:
        pass

def calculateOrderTotals(orderItems):
    grandTotal = 0
    orderTotals = {}

    for orderItem in orderItems:
        itemTotal = orderItem[1] * orderItem[3]

        if orderItem[0] not in orderTotals:
            orderTotals[orderItem[0]] = 0

        orderTotals[orderItem[0]] += itemTotal
        grandTotal += itemTotal

    return {"grandTotal": grandTotal, "orderTotals": orderTotals}