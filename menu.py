from db import db


def addMenuItem(itemName, itemPrice, itemCategory, itemDescription):
    if itemNameIsReserved(itemName):
        return

    try:
        sql = "INSERT INTO menuItems (itemName,itemPrice,itemCategory,itemDescription) VALUES (:itemName,:itemPrice,:itemCategory,:itemDescription)"
        db.session.execute(sql, {"itemName": itemName, "itemPrice": itemPrice,
                                 "itemCategory": itemCategory, "itemDescription": itemDescription})
        db.session.commit()
    except:
        pass


def editMenuItem(id, itemName, itemPrice, itemCategory, itemDescription):
    if itemNameIsReserved(itemName):
        return

    try:
        sql = "UPDATE menuItems SET itemName=:itemName, itemPrice=:itemPrice, itemCategory=:itemCategory, itemDescription=:itemDescription WHERE id = :id"
        db.session.execute(sql, {"itemName": itemName, "itemPrice": itemPrice,
                                "itemCategory": itemCategory, "itemDescription": itemDescription, "id": id})
        db.session.commit()
    except:
        pass

def getMenu():
    sql = "SELECT id, itemName, itemPrice, itemDescription, itemCategory FROM menuItems"
    result = db.session.execute(sql)
    return result.fetchall()

def getMenuItemById(id):
    sql = "SELECT id, itemName, itemPrice, itemCategory, itemDescription FROM menuItems WHERE id = :id"
    result = db.session.execute(sql, {"id": id})
    return result.fetchone()

def itemNameIsReserved(itemName):
    sql = "SELECT id FROM menuItems WHERE itemName=:itemName"
    result = db.session.execute(sql, {"itemName": itemName})
    menuItem = result.fetchone()

    if not menuItem:
        return False

    return True

def getMenuItemCategories():
    sql = "SELECT unnest(enum_range(NULL::menuItemCategory))"
    result = db.session.execute(sql)
    return result.fetchall()

def validItem(itemName, itemPrice, itemDescription):
    return len(itemName) > 5 and len(itemDescription) > 5 and float(itemPrice) >= 0
