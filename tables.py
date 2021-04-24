from db import db
from flask import session
import users

def addTable(tableName, tableWaiter, tableUser):
    if tableNameIsReserved(tableName):
        return

    # Check waiter
    if not users.getUserByTypeAndId("waiter", tableWaiter):
        return

    # Check table user
    if not users.getUserByTypeAndId("table", tableUser):
        return

    # Check that the table user is free
    tablesForUser = getTablesForTableUser(tableUser)
    if len(tablesForUser) > 0:
        return

    try:
        sql = "INSERT INTO tables (tableName,waiterId,userId,wantsToPay) VALUES (:tableName,:tableWaiter,:tableUser, FALSE)"
        db.session.execute(
            sql, {"tableName": tableName, "tableWaiter": tableWaiter, "tableUser": tableUser})
        db.session.commit()
    except:
        pass

def editTable(id, tableName, tableWaiter, tableUser):
    if tableNameIsReserved(tableName):
        return

    # Check waiter
    if not users.getUserByTypeAndId("waiter", tableWaiter):
        return

    # Check table user
    if not users.getUserByTypeAndId("table", tableUser):
        return

    # Check that the table user is free
    tablesForUser = getTablesForTableUser(tableUser)

    if len(tablesForUser) > 0 and tables[0][0] != id:
        return redirect("/")

    try:
        # Update table
        sql = "UPDATE tables SET tableName=:tableName, waiterId=:tableWaiter, userId=:tableUser WHERE id = :id"
        db.session.execute(sql, {
                            "tableName": tableName, "tableWaiter": tableWaiter, "tableUser": tableUser, "id": id})
        db.session.commit()
    except:
        pass
            
def tableNameIsReserved(tableName):
    sql = "SELECT id FROM tables WHERE tableName=:tableName"
    result = db.session.execute(sql, {"tableName": tableName})
    table = result.fetchone()

    if not table:
        return False

    return True

def getTablesForTableUser(tableUser):
    sql = "SELECT id FROM tables WHERE userId = :tableUser"
    result = db.session.execute(sql, {"tableUser": tableUser})
    return result.fetchall()

def getTablesWithWaiters():
    sql = "SELECT t.id, t.tableName, u.username FROM tables t LEFT JOIN users u ON t.waiterId = u.id"
    result = db.session.execute(sql)
    return result.fetchall()

def getTableAndWaiterByTableId(id):
    sql = "SELECT t.id, t.tableName, u.id, t.userId FROM tables t LEFT JOIN users u ON t.waiterId = u.id WHERE t.id=:id"
    result = db.session.execute(sql, {"id": id})
    return result.fetchone()

def getTableIdForUser():
    sql = "SELECT id FROM tables WHERE userId = :userId"
    result = db.session.execute(sql, {"userId": session.get("userId")})
    return result.fetchone()[0]

def getTableAndWaiterForUser():
    sql = "SELECT t.id, t.tableName, u.username, t.wantsToPay FROM tables t LEFT JOIN users u ON t.waiterId = u.id WHERE t.userId=:id"
    result = db.session.execute(sql, {"id": session.get("userId")})
    return result.fetchone()

def getTablesForWaiter():
    sql = "SELECT id, tableName, wantsToPay FROM tables WHERE waiterId = :id"
    result = db.session.execute(sql, {"id": session.get("userId")})
    return result.fetchall()

def setWantsToPay(id, status):
    try:
        sql = "UPDATE tables SET wantsToPay = :status WHERE id = :id"
        db.session.execute(sql, {"id": id, "status": status})
        db.session.commit()
    except:
        pass

