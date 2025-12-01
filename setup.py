from setuptools import setup, find_packages

setup(
    name="mechanics-shop-api",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask>=3.0.0",
        "Flask-SQLAlchemy==3.0.5",
        "Flask-Migrate==4.1.0",
        "Flask-CORS==6.0.1",
        "Flask-Caching==2.3.1",
        "Flask-Limiter==4.0.0",
        "python-dotenv==1.2.1",
        "gunicorn==21.2.0",
        "psycopg2-binary==2.9.11",
        "PyJWT==2.8.0",
        "bcrypt==4.1.2",
    ],
)