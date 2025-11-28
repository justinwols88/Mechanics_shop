"""
Production entry point for Mechanics Shop API
"""

from app import create_app
 # Import the actual class

# Pass the class object, not a string
app = create_app()

if __name__ == '__main__':
    app.run()