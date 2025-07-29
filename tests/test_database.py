import pytest
from unittest.mock import Mock, patch, MagicMock
from app.database import SnowflakeConnection
import snowflake.connector


class TestSnowflakeConnection:
    def setup_method(self):
        """Set up test fixtures."""
        self.db = SnowflakeConnection()

    @patch('app.database.secrets_manager')
    def test_get_credentials_success(self, mock_secrets):
        """Test successful credential retrieval."""
        mock_credentials = {
            "account": "test_account",
            "user": "test_user",
            "password": "test_password",
            "warehouse": "test_warehouse",
            "database": "test_database",
            "schema": "test_schema",
            "role": "test_role"
        }
        mock_secrets.get_snowflake_credentials.return_value = mock_credentials
        
        credentials = self.db._get_credentials()
        assert credentials == mock_credentials
        mock_secrets.get_snowflake_credentials.assert_called_once()

    @patch('app.database.secrets_manager')
    def test_get_credentials_failure(self, mock_secrets):
        """Test credential retrieval failure."""
        mock_secrets.get_snowflake_credentials.side_effect = Exception("Secret not found")
        
        with pytest.raises(Exception) as exc_info:
            self.db._get_credentials()
        
        assert "Secret not found" in str(exc_info.value)

    @patch('app.database.snowflake.connector.connect')
    @patch('app.database.secrets_manager')
    def test_get_connection_success(self, mock_secrets, mock_connect):
        """Test successful database connection."""
        mock_credentials = {
            "account": "test_account",
            "user": "test_user",
            "password": "test_password",
            "warehouse": "test_warehouse",
            "database": "test_database",
            "schema": "test_schema",
            "role": "test_role"
        }
        mock_secrets.get_snowflake_credentials.return_value = mock_credentials
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        with self.db.get_connection() as conn:
            assert conn == mock_connection
            mock_connect.assert_called_once_with(
                account="test_account",
                user="test_user",
                password="test_password",
                warehouse="test_warehouse",
                database="test_database",
                schema="test_schema",
                role="test_role"
            )
        
        mock_connection.close.assert_called_once()

    @patch('app.database.snowflake.connector.connect')
    @patch('app.database.secrets_manager')
    def test_execute_query_success(self, mock_secrets, mock_connect):
        """Test successful query execution."""
        mock_credentials = {"account": "test"}
        mock_secrets.get_snowflake_credentials.return_value = mock_credentials
        
        mock_cursor = MagicMock()
        mock_cursor.description = [("ID",), ("NAME",)]
        mock_cursor.fetchall.return_value = [(1, "John"), (2, "Jane")]
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        result = self.db.execute_query("SELECT * FROM users")
        
        expected_result = [
            {"ID": 1, "NAME": "John"},
            {"ID": 2, "NAME": "Jane"}
        ]
        assert result == expected_result
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users")
        mock_cursor.close.assert_called_once()

    @patch('app.database.snowflake.connector.connect')
    @patch('app.database.secrets_manager')
    def test_execute_query_with_params(self, mock_secrets, mock_connect):
        """Test query execution with parameters."""
        mock_credentials = {"account": "test"}
        mock_secrets.get_snowflake_credentials.return_value = mock_credentials
        
        mock_cursor = MagicMock()
        mock_cursor.description = [("ID",), ("NAME",)]
        mock_cursor.fetchall.return_value = [(1, "John")]
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        params = {"user_id": 1}
        result = self.db.execute_query("SELECT * FROM users WHERE id = %(user_id)s", params)
        
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE id = %(user_id)s", params)
        assert len(result) == 1
        assert result[0]["ID"] == 1

    @patch('app.database.snowflake.connector.connect')
    @patch('app.database.secrets_manager')
    def test_execute_non_query_success(self, mock_secrets, mock_connect):
        """Test successful non-query execution."""
        mock_credentials = {"account": "test"}
        mock_secrets.get_snowflake_credentials.return_value = mock_credentials
        
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        affected_rows = self.db.execute_non_query("INSERT INTO users (name) VALUES ('John')")
        
        assert affected_rows == 1
        mock_cursor.execute.assert_called_once_with("INSERT INTO users (name) VALUES ('John')")
        mock_cursor.close.assert_called_once()

    @patch('app.database.snowflake.connector.connect')
    @patch('app.database.secrets_manager')
    def test_register_user_if_not_exists_new_user(self, mock_secrets, mock_connect):
        """Test registering a new user that doesn't exist."""
        mock_credentials = {"account": "test"}
        mock_secrets.get_snowflake_credentials.return_value = mock_credentials
        
        mock_cursor = MagicMock()
        # First call (check if user exists) - no results
        mock_cursor.fetchone.side_effect = [None, (1, "John Doe", "john@example.com", "2023-01-01")]
        mock_cursor.description = [("ID",), ("NAME",), ("EMAIL",), ("CREATED_AT",)]
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        result = self.db.register_user_if_not_exists("John Doe", "john@example.com")
        
        assert result["created"] is True
        assert result["updated"] is False
        assert result["user"]["NAME"] == "John Doe"
        assert result["user"]["EMAIL"] == "john@example.com"
        assert "New user created" in result["message"]

    @patch('app.database.snowflake.connector.connect')
    @patch('app.database.secrets_manager')
    def test_register_user_if_not_exists_existing_user(self, mock_secrets, mock_connect):
        """Test registering a user that already exists with same name."""
        mock_credentials = {"account": "test"}
        mock_secrets.get_snowflake_credentials.return_value = mock_credentials
        
        mock_cursor = MagicMock()
        # User already exists with same name
        mock_cursor.fetchone.return_value = (1, "John Doe", "john@example.com", "2023-01-01")
        mock_cursor.description = [("ID",), ("NAME",), ("EMAIL",), ("CREATED_AT",)]
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        result = self.db.register_user_if_not_exists("John Doe", "john@example.com")
        
        assert result["created"] is False
        assert result["updated"] is False
        assert result["user"]["NAME"] == "John Doe"
        assert result["user"]["EMAIL"] == "john@example.com"
        assert "already exists" in result["message"]

    @patch('app.database.snowflake.connector.connect')
    @patch('app.database.secrets_manager')
    def test_register_user_if_not_exists_update_name(self, mock_secrets, mock_connect):
        """Test registering a user that exists but with different name."""
        mock_credentials = {"account": "test"}
        mock_secrets.get_snowflake_credentials.return_value = mock_credentials
        
        mock_cursor = MagicMock()
        # First call - user exists with old name, second call - user with updated name
        mock_cursor.fetchone.side_effect = [
            (1, "John Old", "john@example.com", "2023-01-01"),
            (1, "John Updated", "john@example.com", "2023-01-01")
        ]
        mock_cursor.description = [("ID",), ("NAME",), ("EMAIL",), ("CREATED_AT",)]
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        result = self.db.register_user_if_not_exists("John Updated", "john@example.com")
        
        assert result["created"] is False
        assert result["updated"] is True
        assert result["user"]["NAME"] == "John Updated"
        assert result["user"]["EMAIL"] == "john@example.com"
        assert "name updated" in result["message"]
