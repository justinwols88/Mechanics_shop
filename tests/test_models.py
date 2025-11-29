"""
Test database models
"""
import sys
import os

# Add parent directory to Python path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

class TestCustomerModel:
    """Test Customer model"""
    
    def test_customer_attributes(self):
        """Test Customer model has required attributes"""
        from app.models.customer import Customer
        customer = Customer()
        
        assert hasattr(customer, 'id')
        assert hasattr(customer, 'email')
        assert hasattr(customer, 'password_hash')
        assert hasattr(customer, 'first_name')
        assert hasattr(customer, 'last_name')
    
    def test_customer_methods(self):
        """Test Customer model has required methods"""
        from app.models.customer import Customer
        customer = Customer()
        
        assert hasattr(customer, 'set_password')
        assert hasattr(customer, 'check_password')
        assert hasattr(customer, 'generate_token')
        assert hasattr(customer, 'to_dict')

class TestMechanicModel:
    """Test Mechanic model"""
    
    def test_mechanic_attributes(self):
        """Test Mechanic model has required attributes"""
        from app.models.mechanic import Mechanic
        mechanic = Mechanic()
        
        assert hasattr(mechanic, 'id')
        assert hasattr(mechanic, 'email')
        assert hasattr(mechanic, 'first_name')
        assert hasattr(mechanic, 'last_name')
        assert hasattr(mechanic, 'password_hash')
    
    def test_mechanic_methods(self):
        """Test Mechanic model has required methods"""
        from app.models.mechanic import Mechanic
        mechanic = Mechanic()
        
        assert hasattr(mechanic, 'set_password')
        assert hasattr(mechanic, 'check_password')
        assert hasattr(mechanic, 'generate_token')
        assert hasattr(mechanic, 'to_dict')

class TestInventoryModel:
    """Test Inventory model"""
    
    def test_inventory_attributes(self):
        """Test Inventory model has required attributes"""
        from app.models.inventory import Inventory
        inventory = Inventory()
        
        assert hasattr(inventory, 'id')
        assert hasattr(inventory, 'part_name')
        assert hasattr(inventory, 'price')
        assert hasattr(inventory, 'quantity')
    
    def test_inventory_methods(self):
        """Test Inventory model has required methods"""
        from app.models.inventory import Inventory
        inventory = Inventory()
        
        assert hasattr(inventory, 'to_dict')

class TestServiceTicketModel:
    """Test ServiceTicket model"""
    
    def test_service_ticket_attributes(self):
        """Test ServiceTicket model has required attributes"""
        from app.models.service_ticket import ServiceTicket
        ticket = ServiceTicket()
        
        assert hasattr(ticket, 'id')
        assert hasattr(ticket, 'customer_id')
        assert hasattr(ticket, 'vehicle_info')
        assert hasattr(ticket, 'issue_description')
        assert hasattr(ticket, 'status')
    
    def test_service_ticket_methods(self):
        """Test ServiceTicket model has required methods"""
        from app.models.service_ticket import ServiceTicket
        ticket = ServiceTicket()
        
        assert hasattr(ticket, 'to_dict')