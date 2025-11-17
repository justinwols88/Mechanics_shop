# Mechanics Shop API

A Flask-based REST API for managing customers, service tickets, mechanics, and inventory using the **Application Factory Pattern**.

---

## ✅ Features

- **Rate Limiting & Caching**: Flask-Limiter and Flask-Caching
- **Token Authentication**: JWT with python-jose
- **CRUD Operations**: Customers, Service Tickets, Mechanics, Inventory
- **Advanced Queries**:
  - Pagination for customers
  - Mechanics ranking by ticket count
  - Add/remove mechanics from tickets
  - Add inventory parts to tickets
- **Blueprint Structure** for modularity
- **Database Migrations** with Flask-Migrate

---

## ✅ Tech Stack

- Flask
- SQLAlchemy
- Flask-Migrate
- Marshmallow
- Flask-Limiter
- Flask-Caching
- python-jose

---

## ✅ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/mechanics_shop.git
cd mechanics_shop
```

### 2. Create a virtual environment

Shell

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

### 3. Install dependencies

Shell

pip install -r requirements.txt

✅ Database Setup

Option 1: SQLite (Recommended for Development)

Edit config.py:
Python

SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
Run migrations:

Shell

set FLASK_APP=run.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

Option 2: MySQL

Create database:
SQL

CREATE DATABASE mechanics_shop;
Update config.py:
Python

SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/mechanics_shop'
Run migrations:

Shell

set FLASK_APP=run.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

✅ Running the App

Shell

App runs at: <http://127.0.0.1:5000>

✅ API Endpoints

Authentication

POST /customers/login → Login customer
POST /mechanics/login → Login mechanic

Customers

GET /customers/all?page=1&per_page=5 → Paginated customers

Service Tickets

GET /tickets/my-tickets → Customer's tickets (requires token)
PUT /tickets/<"id">/edit → Add/remove mechanics
POST /tickets/<"id">/add-part → Add inventory part to ticket

Mechanics

GET /mechanics/ranking → Mechanics ranked by ticket count

Inventory

POST /inventory/ → Create part
GET /inventory/ → Get all parts
GET /inventory/<"id"> → Get single part
PUT /inventory/<"id"> → Update part
DELETE /inventory/<"id"> → Delete part


✅ Rate Limiting & Caching

Default: 100 requests/hour
Example: /customers/all → 10 requests/minute + cached for 60s


✅ Testing

Use Postman. Import the provided collection below.

---

## ✅ **Postman Collection JSON**

Save this as `Mechanics_Shop.postman_collection.json` and import into Postman:

```json
{
  "info": {
    "name": "Mechanics Shop API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Customer Login",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": { "raw": "http://127.0.0.1:5000/customers/login" },
        "body": {
          "mode": "raw",
          "raw": "{\n    \"email\": \"test@example.com\",\n    \"password\": \"1234\"\n}"
        }
      }
    },
    {
      "name": "Get Customers (Paginated)",
      "request": {
        "method": "GET",
        "url": { "raw": "http://127.0.0.1:5000/customers/all?page=1&per_page=5" }
      }
    },
    {
      "name": "My Tickets",
      "request": {
        "method": "GET",
        "header": [{ "key": "Authorization", "value": "Bearer {{token}}" }],
        "url": { "raw": "http://127.0.0.1:5000/tickets/my-tickets" }
      }
    },
    {
      "name": "Add Part to Ticket",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": { "raw": "http://127.0.0.1:5000/tickets/1/add-part" },
        "body": { "mode": "raw", "raw": "{ \"part_id\": 1 }" }
      }
    },
    {
      "name": "Mechanic Login",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": { "raw": "http://127.0.0.1:5000/mechanics/login" },
        "body": { "mode": "raw", "raw": "{ \"name\": \"John\" }" }
      }
    },
    {
      "name": "Mechanics Ranking",
      "request": {
        "method": "GET",
        "url": { "raw": "http://127.0.0.1:5000/mechanics/ranking" }
      }
    },
    {
      "name": "Create Inventory",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": { "raw": "http://127.0.0.1:5000/inventory/" },
        "body": { "mode": "raw", "raw": "{ \"name\": \"Brake Pad\", \"price\": 49.99 }" }
      }
    },
    {
      "name": "Get All Inventory",
      "request": {
        "method": "GET",
        "url": { "raw": "http://127.0.0.1:5000/inventory/" }
      }
    },
    {
      "name": "Update Inventory",
      "request": {
        "method": "PUT",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": { "raw": "http://127.0.0.1:5000/inventory/1" },
        "body": { "mode": "raw", "raw": "{ \"price\": 59.99 }" }
      }
    },
    {
      "name": "Delete Inventory",
      "request": {
        "method": "DELETE",
        "url": { "raw": "http://127.0.0.1:5000/inventory/1" }
      }
    }
  ]
}
```
