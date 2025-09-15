import pytest
from application import app, get_db


@pytest.fixture
def mock_db(mocker):
    """Mock database connection"""
    mock = mocker.MagicMock()
    # Add mock data for common database queries
    mock.execute.return_value = [
        {
            "id": 1,
            "samplename": "Test Shirt",
            "price": 29.99,
            "onSalePrice": 19.99,
            "image": "sample0.jpg",
            "typeClothes": "shirt",
            "description": "A test shirt",
            "onSale": 1
        }
    ]
    mocker.patch('application.get_db', return_value=mock)
    return mock


@pytest.fixture
def client(mock_db):
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    with app.test_client() as client:
        yield client


def test_app_creation():
    """Test that Flask app can be created"""
    assert app is not None
    assert app.name == 'application'


def test_home_page(client, mock_db):
    """Test that home page loads successfully"""
    rv = client.get('/')
    assert rv.status_code == 200
    # Verify database was queried for shirts
    mock_db.execute.assert_called_with("SELECT * FROM shirts ORDER BY onSalePrice ASC")


def test_login_page(client):
    """Test login page loads"""
    rv = client.get('/login/')
    assert rv.status_code == 200


def test_new_user_page(client):
    """Test new user registration page loads"""
    rv = client.get('/new/')
    assert rv.status_code == 200


def test_database_mock_functionality(mock_db):
    """Test database mock works correctly"""
    db = get_db()
    result = db.execute("SELECT * FROM shirts ORDER BY onSalePrice ASC")
    assert len(result) == 1
    assert result[0]["samplename"] == "Test Shirt"
    assert result[0]["price"] == 29.99


def test_buy_route_requires_parameters(client, mock_db):
    """Test buy route behavior with missing parameters"""
    # This should fail gracefully when parameters are missing
    with pytest.raises(Exception):
        client.get('/buy/')


def test_flask_routes_exist():
    """Test that all expected routes are registered"""
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    expected_routes = [
        "/", "/login/", "/cart/", "/register/", 
        "/new/", "/buy/", "/logout/", "/filter/"
    ]
    
    for route in expected_routes:
        assert route in routes, f"Route {route} not found in registered routes"


def test_app_config_testing_mode():
    """Test app is properly configured for testing"""
    assert app.config['TESTING'] is True