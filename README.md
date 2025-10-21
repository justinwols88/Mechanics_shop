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

## Rate Limiting and Caching

This API includes rate limiting and caching for improved performance and security:

### Rate Limited Endpoints:
- `POST /mechanics/` - 5 requests per minute
- `PUT /mechanics/<id>` - 10 requests per minute  
- `DELETE /mechanics/<id>` - 3 requests per minute
- `POST /service-tickets/` - 10 requests per minute
- Assignment/Removal endpoints - 20 requests per minute

### Cached Endpoints:
- `GET /mechanics/` - Cached for 60 seconds
- `GET /service-tickets/` - Cached for 30 seconds

### Why These Choices:

**Rate Limiting Reasons:**
- **Creation endpoints**: Prevent spam and automated data injection
- **Update endpoints**: Prevent rapid, potentially malicious modifications
- **Deletion endpoints**: Protect against mass deletion attacks
- **Assignment endpoints**: Control frequent relationship changes

**Caching Reasons:**
- **GET /mechanics**: Mechanic data changes infrequently, longer cache period
- **GET /service-tickets**: Ticket data changes more often, shorter cache period
- Both reduce database load and improve response times for frequently accessed data

this assignment was created with :heart: Justin Wold
