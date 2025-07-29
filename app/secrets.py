import json
import boto3
from typing import Dict, Any
from botocore.exceptions import ClientError
from app.config import settings


class SecretsManager:
    def __init__(self):
        self.client = boto3.client('secretsmanager', region_name=settings.aws_region)
    
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """
        Retrieve a secret from AWS Secrets Manager.
        
        Args:
            secret_name: The name of the secret to retrieve
            
        Returns:
            Dictionary containing the secret values
            
        Raises:
            Exception: If the secret cannot be retrieved
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return json.loads(response['SecretString'])
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'DecryptionFailureException':
                raise Exception("Secrets Manager can't decrypt the protected secret text using the provided KMS key.")
            elif error_code == 'InternalServiceErrorException':
                raise Exception("An error occurred on the server side.")
            elif error_code == 'InvalidParameterException':
                raise Exception("You provided an invalid value for a parameter.")
            elif error_code == 'InvalidRequestException':
                raise Exception("You provided a parameter value that is not valid for the current state of the resource.")
            elif error_code == 'ResourceNotFoundException':
                raise Exception(f"The requested secret {secret_name} was not found.")
            else:
                raise e
    
    def get_snowflake_credentials(self) -> Dict[str, str]:
        """
        Get Snowflake credentials from AWS Secrets Manager.
        
        Returns:
            Dictionary containing Snowflake connection parameters
        """
        return self.get_secret(settings.aws_secret_name)


secrets_manager = SecretsManager()
