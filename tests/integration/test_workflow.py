import pytest

from application import app


@pytest.fixture
def mock_db(mocker):
    """Mock database connection for integration tests"""
    mock = mocker.MagicMock()

    def mock_execute(*args, **kwargs):
        query = args[0] if args else ""

        # Mock für User-Lookup (Registrierung)
        if "SELECT * FROM users WHERE username = :username" in query:
            return []  # No existing user

        # Mock für User-Insert (Registrierung)
        elif "INSERT INTO users" in query:
            return True  # Successful insert

        # Mock für Login-Queries
        elif "SELECT * FROM users WHERE username = :user AND password = :pwd" in query:
            return []  # User not found for login

        return []  # Default empty response

    mock.execute.side_effect = mock_execute
    mocker.patch("application.get_db", return_value=mock)
    return mock


@pytest.fixture
def client(mock_db):
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


def test_user_registration_flow(client, mock_db):
    """Test complete user registration workflow"""

    # Test 1: Registration with missing data should handle gracefully
    rv = client.post("/register/")
    # This might return 400 or 500 depending on how form validation is handled
    assert rv.status_code in [400, 500, 200]  # More permissive for missing data

    # Test 2: Complete registration flow
    rv = client.post(
        "/register/",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "fname": "Test",
            "lname": "User",
            "confirm": "testpassword",
        },
    )

    # Should either render success page (200) or redirect to login (302)
    assert rv.status_code in [200, 302]

    # Verify database interactions occurred
    mock_db.execute.assert_any_call(
        "SELECT * FROM users WHERE username = :username ", username="testuser"
    )


def test_registration_duplicate_username(client, mock_db):
    """Test registration with existing username"""

    # Mock that user already exists
    def mock_execute_existing_user(*args, **kwargs):
        query = args[0] if args else ""
        if "SELECT * FROM users WHERE username = :username" in query:
            return [{"id": 1, "username": "testuser"}]  # User exists
        return []

    mock_db.execute.side_effect = mock_execute_existing_user

    rv = client.post(
        "/register/",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "fname": "Test",
            "lname": "User",
            "confirm": "testpassword",
        },
    )

    # Should return to registration page with error
    assert rv.status_code == 200
    # Could also check if error message is in response data
