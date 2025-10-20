# Mechanic Shop API

A Flask-based REST API for managing a mechanic shop with mechanics and service tickets.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Set up the database:
   ```bash
   flask db upgrade 
4. Run the application:
   ```bash  flask run
   flask run
    ```
## API Endpoints
Mechanics
POST /mechanics/ - Create a new mechanic

GET /mechanics/ - Get all mechanics

PUT /mechanics/<id> - Update a mechanic

DELETE /mechanics/<id> - Delete a mechanic

Service Tickets
POST /service-tickets/ - Create a new service ticket

GET /service-tickets/ - Get all service tickets

PUT /service-tickets/<ticket_id>/assign-mechanic/<mechanic_id> - Assign mechanic to ticket

PUT /service-tickets/<ticket_id>/remove-mechanic/<mechanic_id> - Remove mechanic from ticket

1. Create Mechanic
2. Get All Mechanics
3. Update Mechanic
4. Delete Mechanic
5. Create Service Ticket
6. Get All Service Tickets
7. Assign Mechanic to Ticket
8. Remove Mechanic from Ticket


this assignment was created with :heart: Justin Wold