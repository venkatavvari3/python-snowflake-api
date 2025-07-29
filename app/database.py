import snowflake.connector
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
from app.secrets import secrets_manager
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class SnowflakeConnection:
    def __init__(self):
        self._connection = None
        self._credentials = None
    
    def _get_credentials(self) -> Dict[str, str]:
        """Get Snowflake credentials from AWS Secrets Manager."""
        if not self._credentials:
            try:
                self._credentials = secrets_manager.get_snowflake_credentials()
            except Exception as e:
                logger.error(f"Failed to retrieve Snowflake credentials: {str(e)}")
                raise
        return self._credentials
    
    @contextmanager
    def get_connection(self):
        """Context manager for Snowflake database connections."""
        connection = None
        try:
            credentials = self._get_credentials()
            
            connection = snowflake.connector.connect(
                account=credentials.get('account'),
                user=credentials.get('user'),
                password=credentials.get('password'),
                warehouse=credentials.get('warehouse'),
                database=credentials.get('database'),
                schema=credentials.get('schema'),
                role=credentials.get('role')
            )
            
            yield connection
            
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results as a list of dictionaries.
        
        Args:
            query: SQL query to execute
            params: Optional parameters for the query
            
        Returns:
            List of dictionaries representing query results
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                
                # Fetch all results and convert to list of dictionaries
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
                
            finally:
                cursor.close()
    
    def execute_non_query(self, query: str, params: Optional[Dict] = None) -> int:
        """
        Execute a non-query statement (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL statement to execute
            params: Optional parameters for the query
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                return cursor.rowcount
                
            finally:
                cursor.close()
    
    def register_user_if_not_exists(self, name: str, email: str) -> Dict[str, Any]:
        """
        Register a user if they don't exist, or return existing user.
        
        Args:
            name: User's name
            email: User's email address
            
        Returns:
            Dictionary with user data and creation status
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Check if user exists
                check_query = """
                SELECT id, name, email, created_at 
                FROM users 
                WHERE email = %(email)s
                """
                
                cursor.execute(check_query, {"email": email})
                existing_user = cursor.fetchone()
                
                if existing_user:
                    # User exists, check if we need to update the name
                    columns = [desc[0] for desc in cursor.description]
                    user_data = dict(zip(columns, existing_user))
                    
                    if user_data.get("NAME") != name:
                        # Update the name
                        update_query = """
                        UPDATE users 
                        SET name = %(name)s 
                        WHERE email = %(email)s
                        """
                        cursor.execute(update_query, {"name": name, "email": email})
                        
                        # Get updated user data
                        cursor.execute(check_query, {"email": email})
                        updated_user = cursor.fetchone()
                        user_data = dict(zip(columns, updated_user))
                        
                        return {
                            "user": user_data,
                            "created": False,
                            "updated": True,
                            "message": f"User already existed, name updated to {name}"
                        }
                    
                    return {
                        "user": user_data,
                        "created": False,
                        "updated": False,
                        "message": f"User already exists with email {email}"
                    }
                
                # User doesn't exist, create new user
                insert_query = """
                INSERT INTO users (name, email, created_at) 
                VALUES (%(name)s, %(email)s, CURRENT_TIMESTAMP())
                """
                
                cursor.execute(insert_query, {"name": name, "email": email})
                
                # Get the created user
                cursor.execute(check_query, {"email": email})
                new_user = cursor.fetchone()
                columns = [desc[0] for desc in cursor.description]
                user_data = dict(zip(columns, new_user))
                
                return {
                    "user": user_data,
                    "created": True,
                    "updated": False,
                    "message": f"New user created with email {email}"
                }
                
            finally:
                cursor.close()


# Global instance
snowflake_db = SnowflakeConnection()
