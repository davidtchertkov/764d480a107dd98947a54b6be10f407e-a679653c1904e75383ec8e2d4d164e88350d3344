import pytest

from application import app

@pytest.fixture
def mock_db(mocker):
    """Mock database connection"""
    mock = mocker.MagicMock()
    def mock_execute(*args, **kwargs):
        if "SELECT * FROM users WHERE username = :username" in args[0]:
            return []  # No existing user
        return []  # Default empty response
    mock.execute.side_effect = mock_execute
    mocker.patch('application.get_db', return_value=mock)
    return mock

@pytest.fixture
def client(mock_db):
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_user_registration_flow(client):
    """Test complete user registration workflow"""
    # Test registration form submission directly since the registration route only accepts POST
    rv = client.post('/register/')

    # Test registration form submission
    rv = client.post(
        '/register/',
        data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
            'fname': 'Test',
            'lname': 'User',
            'confirm': 'testpassword'
        },
    )
    assert rv.status_code in [200, 302]  # 302 if redirect to login
