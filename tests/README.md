# Mechanics Shop API Tests

## Test Structure

- `test_basic.py` - Basic environment tests
- `test_models.py` - Database model tests  
- `test_app.py` - Application creation tests
- `test_app_integration.py` - API endpoint tests

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_models.py -v

# Run with coverage
python -m pytest tests/ -v --cov=app
