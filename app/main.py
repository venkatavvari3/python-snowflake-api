from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import time
import logging

from app.config import settings
from app.database import snowflake_db
from app.models import (
    HealthCheck, QueryRequest, QueryResponse, ErrorResponse,
    User, UserCreate, UserUpdate, UserRegistrationResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="A FastAPI application with Snowflake integration for AWS Lambda deployment"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            timestamp=datetime.now()
        ).dict()
    )


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.api_version
    )


@app.get("/health/database")
async def database_health_check():
    """Database health check endpoint."""
    try:
        # Simple query to test database connection
        result = snowflake_db.execute_query("SELECT 1 as test")
        if result and result[0].get("TEST") == 1:
            return {"status": "healthy", "database": "connected", "timestamp": datetime.now()}
        else:
            raise HTTPException(status_code=503, detail="Database connection test failed")
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def execute_query(query_request: QueryRequest):
    """Execute a custom SQL query."""
    try:
        start_time = time.time()
        
        # Execute the query
        results = snowflake_db.execute_query(
            query_request.query,
            query_request.parameters
        )
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return QueryResponse(
            data=results,
            row_count=len(results),
            execution_time_ms=round(execution_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Query execution failed: {str(e)}")


@app.get("/users", response_model=List[User])
async def get_users(limit: Optional[int] = 100):
    """Get all users from the database."""
    try:
        query = """
        SELECT id, name, email, created_at 
        FROM users 
        ORDER BY created_at DESC 
        LIMIT %(limit)s
        """
        
        results = snowflake_db.execute_query(query, {"limit": limit})
        
        # Convert results to User models
        users = []
        for row in results:
            users.append(User(
                id=row.get("ID"),
                name=row.get("NAME"),
                email=row.get("EMAIL"),
                created_at=row.get("CREATED_AT")
            ))
        
        return users
        
    except Exception as e:
        logger.error(f"Get users failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {str(e)}")


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get a specific user by ID."""
    try:
        query = """
        SELECT id, name, email, created_at 
        FROM users 
        WHERE id = %(user_id)s
        """
        
        results = snowflake_db.execute_query(query, {"user_id": user_id})
        
        if not results:
            raise HTTPException(status_code=404, detail="User not found")
        
        row = results[0]
        return User(
            id=row.get("ID"),
            name=row.get("NAME"),
            email=row.get("EMAIL"),
            created_at=row.get("CREATED_AT")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user: {str(e)}")


@app.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user if they don't already exist."""
    try:
        # First check if user already exists by email
        check_query = """
        SELECT id, name, email, created_at 
        FROM users 
        WHERE email = %(email)s
        """
        
        existing_users = snowflake_db.execute_query(check_query, {"email": user.email})
        
        # If user already exists, return the existing user
        if existing_users:
            logger.info(f"User with email {user.email} already exists, returning existing user")
            row = existing_users[0]
            return User(
                id=row.get("ID"),
                name=row.get("NAME"),
                email=row.get("EMAIL"),
                created_at=row.get("CREATED_AT")
            )
        
        # User doesn't exist, create new user
        logger.info(f"Creating new user with email {user.email}")
        insert_query = """
        INSERT INTO users (name, email, created_at) 
        VALUES (%(name)s, %(email)s, CURRENT_TIMESTAMP())
        """
        
        snowflake_db.execute_non_query(insert_query, {
            "name": user.name,
            "email": user.email
        })
        
        # Get the created user
        select_query = """
        SELECT id, name, email, created_at 
        FROM users 
        WHERE email = %(email)s 
        ORDER BY created_at DESC 
        LIMIT 1
        """
        
        results = snowflake_db.execute_query(select_query, {"email": user.email})
        
        if not results:
            raise HTTPException(status_code=500, detail="Failed to retrieve created user")
        
        row = results[0]
        return User(
            id=row.get("ID"),
            name=row.get("NAME"),
            email=row.get("EMAIL"),
            created_at=row.get("CREATED_AT")
        )
        
    except Exception as e:
        logger.error(f"Create user failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserUpdate):
    """Update an existing user."""
    try:
        # Build dynamic update query
        update_fields = []
        params = {"user_id": user_id}
        
        if user_update.name is not None:
            update_fields.append("name = %(name)s")
            params["name"] = user_update.name
        
        if user_update.email is not None:
            update_fields.append("email = %(email)s")
            params["email"] = user_update.email
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_query = f"""
        UPDATE users 
        SET {', '.join(update_fields)}
        WHERE id = %(user_id)s
        """
        
        rows_affected = snowflake_db.execute_non_query(update_query, params)
        
        if rows_affected == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return updated user
        return await get_user(user_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete a user."""
    try:
        delete_query = "DELETE FROM users WHERE id = %(user_id)s"
        
        rows_affected = snowflake_db.execute_non_query(delete_query, {"user_id": user_id})
        
        if rows_affected == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": f"User {user_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")


@app.post("/users/register", response_model=UserRegistrationResponse)
async def register_user(user: UserCreate):
    """Register a new user or return existing user if email already exists."""
    try:
        # Use the dedicated database method for registration
        result = snowflake_db.register_user_if_not_exists(user.name, user.email)
        
        # Extract user data
        user_data = result["user"]
        user_obj = User(
            id=user_data.get("ID"),
            name=user_data.get("NAME"),
            email=user_data.get("EMAIL"),
            created_at=user_data.get("CREATED_AT")
        )
        
        return UserRegistrationResponse(
            user=user_obj,
            created=result["created"],
            message=result["message"]
        )
        
    except Exception as e:
        logger.error(f"Register user failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
