# Restaurant Self-service
Project for TsohaLabra

## Description
The application provides capability for a restaurant to offer self-service for tables.

Features:
- Admin user that can
  - create/modify other users
  - assign server users to tables
  - add/modify menu items for ordering
- Server user that can
  - see active orders from tables the user has been assigned to
  - mark orders as completed
  - mark a bill as paid
- Table user that can
  - see the currently accrued bill (orders with items and total cost)
  - create orders for the table
  - ask the server for a bill

## Usage

Test URL: https://restaurant-selfservice.herokuapp.com/

### As an admin

You can try creating/modifying users and tables as admin (see section Users).

For each table a unique table user is required, but a waiter can have 0..n tables - the application should complain if you try to create a table without a free table user.

### As a waiter

You can see orders for your tables in different states (new, in progress and completed) and you can cancel orders that are in state new. You can proceed orders in state new to state in progress and order in state in progress to state completed.

You can see all your tables below orders and if a table has asked for a bill, you can mark a bill as paid. This also marks all orders for the table as "paid", effectively making the table free again as those orders won't be visible for the table or the waiter and won't be taken into account in any calculations.

### As table user

You can see your own table and your assigned waiter. You can make an order and see its state and cancel it if it has not been accepted yet (status = new). You can ask for the bill, which automatically cancels all your orders that have not been accepted yet.

### Users 
For convenience, a list of default users have been created. Password is identical to username.

- admin1
- waiter1
- table1

## TODO:
- Menu items visible per section for admin (done for ordering already)
- Better styles
- Deletion of things (maybe?)
