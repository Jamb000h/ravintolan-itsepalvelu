DROP TABLE orderItems;

DROP TABLE orders;

DROP TABLE menuItems;

DROP TABLE tables;

DROP TABLE users;

DROP TYPE orderStatus;

DROP TYPE userType;

DROP TYPE menuItemCategory;

CREATE TYPE userType AS ENUM ('admin', 'waiter', 'table');

CREATE TYPE orderStatus as ENUM ('new', 'editing', 'inprogress', 'cancelled', 'completed', 'paid');

CREATE TYPE menuItemCategory as ENUM ('appetizer', 'main', 'dessert', 'beverage');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    userType userType NOT NULL
);

CREATE TABLE tables (
    id SERIAL PRIMARY KEY,
    tableName TEXT UNIQUE NOT NULL,
    waiterId INTEGER REFERENCES users,
    userId INTEGER UNIQUE REFERENCES users
);

CREATE TABLE menuItems (
    id SERIAL PRIMARY KEY,
    itemName TEXT NOT NULL UNIQUE,
    itemPrice NUMERIC NOT NULL,
    itemDescription TEXT,
    itemCategory menuItemCategory NOT NULL
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    tableId INTEGER NOT NULL REFERENCES tables,
    orderStatus orderStatus NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE orderItems (
    orderId INTEGER NOT NULL REFERENCES orders,
    menuItemId INTEGER NOT NULL REFERENCES menuItems,
    quantity INTEGER NOT NULL,
    CONSTRAINT orderItemKey PRIMARY KEY (orderId, menuItemId)
);