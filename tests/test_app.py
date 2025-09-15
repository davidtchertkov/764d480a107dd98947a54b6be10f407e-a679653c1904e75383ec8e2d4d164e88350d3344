import pytest
# pytest-mock is automatically imported
from application import app


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
            "description": "A test shirt"
        }
    ]
    mocker.patch('application.get_db', return_value=mock)
    return mock


@pytest.fixture
def client(mock_db):
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page(client, mock_db):
    """Test that home page loads successfully"""
    rv = client.get('/')
    assert rv.status_code == 200
    # Verify database was queried
    mock_db.execute.assert_called_with("SELECT * FROM shirts ORDER BY onSalePrice")
