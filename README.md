# Restaurant Self-service
Project for TsohaLabra

## Description
The application provides capability for a restaurant to offer self-service for tables.

Features:
- Super user (Restaurant) that can
  - create/modify/delete other users
  - assign server users to tables
  - add/modify/delete menu items for ordering
- Server user that can
  - see active orders from tables the user has been assigned to
  - mark orders as completed
  - mark their own tables free (flag an open bill as paid)
- Table user that can
  - see the currently accrued bill (items and total cost)
  - create orders for the table
  - ask the server for a bill

Currently identified objects:
- User
- Table
- Menu item
- Order
- Bill
