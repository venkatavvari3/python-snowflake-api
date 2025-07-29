import pytest
from unittest.mock import Mock, patch
from app.secrets import SecretsManager, secrets_manager
from botocore.exceptions import ClientError


class TestSecretsManager:
    @patch('app.secrets.boto3.client')
    def setup_method(self, mock_boto_client):
        """Set up test fixtures."""
        self.mock_client = Mock()
        mock_boto_client.return_value = self.mock_client
        self.secrets_mgr = SecretsManager()

    @patch('app.secrets.boto3.client')
    def test_get_secret_success(self, mock_boto_client):
        """Test successful secret retrieval."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        mock_response = {
            'SecretString': '{"username": "test_user", "password": "test_password"}'
        }
        mock_client.get_secret_value.return_value = mock_response
        
        secrets_mgr = SecretsManager()
        result = secrets_mgr.get_secret("test-secret")
        
        expected_result = {"username": "test_user", "password": "test_password"}
        assert result == expected_result
        mock_client.get_secret_value.assert_called_once_with(SecretId="test-secret")

    @patch('app.secrets.boto3.client')
    def test_get_secret_not_found(self, mock_boto_client):
        """Test secret not found error."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        error_response = {'Error': {'Code': 'ResourceNotFoundException'}}
        mock_client.get_secret_value.side_effect = ClientError(error_response, 'GetSecretValue')
        
        secrets_mgr = SecretsManager()
        with pytest.raises(Exception) as exc_info:
            secrets_mgr.get_secret("non-existent-secret")
        
        assert "was not found" in str(exc_info.value)

    @patch('app.secrets.boto3.client')
    def test_get_secret_decryption_failure(self, mock_boto_client):
        """Test decryption failure error."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        error_response = {'Error': {'Code': 'DecryptionFailureException'}}
        mock_client.get_secret_value.side_effect = ClientError(error_response, 'GetSecretValue')
        
        secrets_mgr = SecretsManager()
        with pytest.raises(Exception) as exc_info:
            secrets_mgr.get_secret("test-secret")
        
        assert "can't decrypt" in str(exc_info.value)

    @patch('app.secrets.boto3.client')
    def test_get_secret_internal_error(self, mock_boto_client):
        """Test internal service error."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        error_response = {'Error': {'Code': 'InternalServiceErrorException'}}
        mock_client.get_secret_value.side_effect = ClientError(error_response, 'GetSecretValue')
        
        secrets_mgr = SecretsManager()
        with pytest.raises(Exception) as exc_info:
            secrets_mgr.get_secret("test-secret")
        
        assert "server side" in str(exc_info.value)

    @patch('app.secrets.boto3.client')
    def test_get_secret_invalid_parameter(self, mock_boto_client):
        """Test invalid parameter error."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        error_response = {'Error': {'Code': 'InvalidParameterException'}}
        mock_client.get_secret_value.side_effect = ClientError(error_response, 'GetSecretValue')
        
        secrets_mgr = SecretsManager()
        with pytest.raises(Exception) as exc_info:
            secrets_mgr.get_secret("test-secret")
        
        assert "invalid value" in str(exc_info.value)

    @patch('app.secrets.boto3.client')
    def test_get_secret_invalid_request(self, mock_boto_client):
        """Test invalid request error."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        error_response = {'Error': {'Code': 'InvalidRequestException'}}
        mock_client.get_secret_value.side_effect = ClientError(error_response, 'GetSecretValue')
        
        secrets_mgr = SecretsManager()
        with pytest.raises(Exception) as exc_info:
            secrets_mgr.get_secret("test-secret")
        
        assert "not valid for the current state" in str(exc_info.value)

    @patch.object(SecretsManager, 'get_secret')
    def test_get_snowflake_credentials(self, mock_get_secret):
        """Test getting Snowflake credentials."""
        mock_credentials = {
            "account": "test_account",
            "user": "test_user",
            "password": "test_password",
            "warehouse": "test_warehouse",
            "database": "test_database",
            "schema": "test_schema",
            "role": "test_role"
        }
        mock_get_secret.return_value = mock_credentials
        
        secrets_mgr = SecretsManager()
        result = secrets_mgr.get_snowflake_credentials()
        
        assert result == mock_credentials
        mock_get_secret.assert_called_once_with("snowflake-credentials")
