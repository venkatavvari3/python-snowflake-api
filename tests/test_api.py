import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    @patch('app.main.snowflake_db')
    def test_database_health_check_success(self, mock_db):
        """Test database health check with successful connection."""
        mock_db.execute_query.return_value = [{"TEST": 1}]
        
        response = client.get("/health/database")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    @patch('app.main.snowflake_db')
    def test_database_health_check_failure(self, mock_db):
        """Test database health check with connection failure."""
        mock_db.execute_query.side_effect = Exception("Connection failed")
        
        response = client.get("/health/database")
        assert response.status_code == 503
        data = response.json()
        assert "Database connection failed" in data["detail"]


class TestQueryEndpoint:
    @patch('app.main.snowflake_db')
    def test_execute_query_success(self, mock_db):
        """Test successful query execution."""
        mock_result = [{"id": 1, "name": "test"}]
        mock_db.execute_query.return_value = mock_result
        
        query_data = {
            "query": "SELECT * FROM test_table",
            "parameters": None
        }
        
        response = client.post("/query", json=query_data)
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == mock_result
        assert data["row_count"] == 1
        assert "execution_time_ms" in data

    @patch('app.main.snowflake_db')
    def test_execute_query_failure(self, mock_db):
        """Test query execution failure."""
        mock_db.execute_query.side_effect = Exception("Query failed")
        
        query_data = {
            "query": "SELECT * FROM invalid_table"
        }
        
        response = client.post("/query", json=query_data)
        assert response.status_code == 400
        data = response.json()
        assert "Query execution failed" in data["detail"]


class TestUserEndpoints:
    @patch('app.main.snowflake_db')
    def test_get_users_success(self, mock_db):
        """Test getting users successfully."""
        mock_users = [
            {"ID": 1, "NAME": "John Doe", "EMAIL": "john@example.com", "CREATED_AT": "2023-01-01"},
            {"ID": 2, "NAME": "Jane Smith", "EMAIL": "jane@example.com", "CREATED_AT": "2023-01-02"}
        ]
        mock_db.execute_query.return_value = mock_users
        
        response = client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "John Doe"
        assert data[1]["name"] == "Jane Smith"

    @patch('app.main.snowflake_db')
    def test_get_user_by_id_success(self, mock_db):
        """Test getting a specific user by ID."""
        mock_user = [{"ID": 1, "NAME": "John Doe", "EMAIL": "john@example.com", "CREATED_AT": "2023-01-01"}]
        mock_db.execute_query.return_value = mock_user
        
        response = client.get("/users/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"

    @patch('app.main.snowflake_db')
    def test_get_user_by_id_not_found(self, mock_db):
        """Test getting a user that doesn't exist."""
        mock_db.execute_query.return_value = []
        
        response = client.get("/users/999")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "User not found"

    @patch('app.main.snowflake_db')
    def test_create_user_success(self, mock_db):
        """Test creating a new user."""
        mock_created_user = [{"ID": 1, "NAME": "John Doe", "EMAIL": "john@example.com", "CREATED_AT": "2023-01-01"}]
        mock_db.execute_non_query.return_value = 1
        mock_db.execute_query.return_value = mock_created_user
        
        user_data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        response = client.post("/users", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"

    @patch('app.main.snowflake_db')
    def test_update_user_success(self, mock_db):
        """Test updating a user."""
        mock_updated_user = [{"ID": 1, "NAME": "John Updated", "EMAIL": "john.updated@example.com", "CREATED_AT": "2023-01-01"}]
        mock_db.execute_non_query.return_value = 1
        mock_db.execute_query.return_value = mock_updated_user
        
        update_data = {
            "name": "John Updated",
            "email": "john.updated@example.com"
        }
        
        response = client.put("/users/1", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Updated"
        assert data["email"] == "john.updated@example.com"

    @patch('app.main.snowflake_db')
    def test_update_user_not_found(self, mock_db):
        """Test updating a user that doesn't exist."""
        mock_db.execute_non_query.return_value = 0
        
        update_data = {
            "name": "John Updated"
        }
        
        response = client.put("/users/999", json=update_data)
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "User not found"

    @patch('app.main.snowflake_db')
    def test_delete_user_success(self, mock_db):
        """Test deleting a user."""
        mock_db.execute_non_query.return_value = 1
        
        response = client.delete("/users/1")
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]

    @patch('app.main.snowflake_db')
    def test_delete_user_not_found(self, mock_db):
        """Test deleting a user that doesn't exist."""
        mock_db.execute_non_query.return_value = 0
        
        response = client.delete("/users/999")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "User not found"

    @patch('app.main.snowflake_db')
    def test_register_user_new(self, mock_db):
        """Test registering a new user."""
        mock_result = {
            "user": {"ID": 1, "NAME": "John Doe", "EMAIL": "john@example.com", "CREATED_AT": "2023-01-01"},
            "created": True,
            "message": "New user created with email john@example.com"
        }
        mock_db.register_user_if_not_exists.return_value = mock_result
        
        user_data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["name"] == "John Doe"
        assert data["user"]["email"] == "john@example.com"
        assert data["created"] is True
        assert "New user created" in data["message"]

    @patch('app.main.snowflake_db')
    def test_register_user_existing(self, mock_db):
        """Test registering an existing user."""
        mock_result = {
            "user": {"ID": 1, "NAME": "John Doe", "EMAIL": "john@example.com", "CREATED_AT": "2023-01-01"},
            "created": False,
            "message": "User already exists with email john@example.com"
        }
        mock_db.register_user_if_not_exists.return_value = mock_result
        
        user_data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["name"] == "John Doe"
        assert data["user"]["email"] == "john@example.com"
        assert data["created"] is False
        assert "already exists" in data["message"]

    @patch('app.main.snowflake_db')
    def test_register_user_update_name(self, mock_db):
        """Test registering a user with updated name."""
        mock_result = {
            "user": {"ID": 1, "NAME": "John Updated", "EMAIL": "john@example.com", "CREATED_AT": "2023-01-01"},
            "created": False,
            "message": "User already existed, name updated to John Updated"
        }
        mock_db.register_user_if_not_exists.return_value = mock_result
        
        user_data = {
            "name": "John Updated",
            "email": "john@example.com"
        }
        
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["name"] == "John Updated"
        assert data["user"]["email"] == "john@example.com"
        assert data["created"] is False
        assert "name updated" in data["message"]
