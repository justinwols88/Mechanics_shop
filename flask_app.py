"""
Production entry point for Mechanics Shop API
"""

from app import create_app


app = create_app("ProductionConfig")

if __name__ == '__main__':
    app.run()
