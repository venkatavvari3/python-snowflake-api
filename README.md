# FastAPI Snowflake API

A modern, serverless Python FastAPI application with Snowflake database integration, deployed on AWS Lambda with infrastructure managed by Terraform.

## Features

- 🚀 **FastAPI**: Modern, fast web framework with automatic API documentation
- ❄️ **Snowflake Integration**: Secure connection to Snowflake data platform
- ⚡ **AWS Lambda**: Serverless deployment for cost-effective scaling
- 🔐 **AWS Secrets Manager**: Secure credential management
- 🧪 **Comprehensive Testing**: Full test coverage with Pytest
- 🏗️ **Infrastructure as Code**: Complete Terraform configuration
- 📊 **Monitoring**: CloudWatch integration for logging and monitoring

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌───────────────────┐
│   API Gateway   │───▶│   AWS Lambda     │───▶│   Snowflake DB    │
│                 │    │   (FastAPI)      │    │                   │
└─────────────────┘    └──────────────────┘    └───────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Secrets Manager │
                       │  (Credentials)   │
                       └──────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- AWS CLI configured
- Terraform installed
- Snowflake account with appropriate permissions

### 1. Clone and Setup

```bash
git clone <repository-url>
cd python-snowflake-api

# Copy environment template
cp .env.example .env

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `.env` file with your settings:

```env
AWS_REGION=us-east-1
AWS_SECRET_NAME=your-secret-name
# Add other configuration as needed
```

### 3. Setup Snowflake

Run the SQL setup script in your Snowflake environment:

```sql
-- See sql/setup.sql for complete setup
CREATE OR REPLACE TABLE users (
    id INT AUTOINCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

### 4. Configure Secrets

Store your Snowflake credentials in AWS Secrets Manager:

```json
{
    "account": "your-snowflake-account",
    "user": "your-username",
    "password": "your-password",
    "warehouse": "your-warehouse",
    "database": "your-database",
    "schema": "your-schema",
    "role": "your-role"
}
```

### 5. Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply infrastructure
terraform apply
```

### 6. Test the API

```bash
# Run tests
pytest

# Start local development server
uvicorn app.main:app --reload
```

## API Endpoints

### Health Checks
- `GET /health` - Application health status
- `GET /health/database` - Database connectivity check

### User Management
- `GET /users` - List all users
- `GET /users/{id}` - Get user by ID
- `POST /users` - Create new user (checks if exists first)
- `POST /users/register` - Register user (creates if not exists, updates name if different)
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

### Custom Queries
- `POST /query` - Execute custom SQL queries

### Example Usage

```bash
# Get all users
curl https://your-api-url/users

# Create a new user
curl -X POST https://your-api-url/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Register a user (safer - won't fail if user exists)
curl -X POST https://your-api-url/users/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Execute custom query
curl -X POST https://your-api-url/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT COUNT(*) as user_count FROM users"}'
```

## User Registration Behavior

The application provides two endpoints for user creation:

### `/users` (POST)
- Creates a new user if email doesn't exist
- Returns existing user if email already exists  
- Updates existing user's name if different from provided name
- Always returns a `User` object

### `/users/register` (POST) 
- **Recommended for user registration**
- Creates a new user if email doesn't exist
- Returns existing user if email already exists
- Updates existing user's name if different from provided name
- Returns a `UserRegistrationResponse` with:
  - `user`: The user object
  - `created`: Boolean indicating if user was newly created
  - `message`: Descriptive message about the operation

#### Example Registration Response

```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2023-01-01T12:00:00"
  },
  "created": true,
  "message": "New user created with email john@example.com"
}
```

For existing users:
```json
{
  "user": {
    "id": 1,
    "name": "John Updated",
    "email": "john@example.com", 
    "created_at": "2023-01-01T12:00:00"
  },
  "created": false,
  "message": "User already existed, name updated to John Updated"
}
```

## Development

### Project Structure

```
├── app/                    # FastAPI application
│   ├── __init__.py
│   ├── main.py            # Main FastAPI app
│   ├── config.py          # Configuration settings
│   ├── database.py        # Snowflake connection logic
│   ├── models.py          # Pydantic models
│   ├── secrets.py         # AWS Secrets Manager integration
│   └── lambda_handler.py  # Lambda entry point
├── tests/                 # Test suites
│   ├── test_api.py        # API endpoint tests
│   ├── test_database.py   # Database tests
│   └── test_secrets.py    # Secrets manager tests
├── terraform/             # Infrastructure as code
│   ├── main.tf            # Main Terraform configuration
│   ├── variables.tf       # Input variables
│   ├── outputs.tf         # Output values
│   ├── lambda.tf          # Lambda function configuration
│   ├── api_gateway.tf     # API Gateway setup
│   ├── iam.tf             # IAM roles and policies
│   └── secrets.tf         # Secrets Manager resources
├── scripts/               # Build and deployment scripts
│   ├── build.sh           # Unix build script
│   └── build.bat          # Windows build script
├── sql/                   # Database setup scripts
│   └── setup.sql          # Table creation and sample data
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
└── README.md             # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

### Local Development

```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
open http://localhost:8000/docs
```

### Building for Deployment

```bash
# Linux/macOS
./scripts/build.sh

# Windows
scripts\build.bat

# Build and deploy
./scripts/build.sh --deploy
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | `us-east-1` |
| `AWS_SECRET_NAME` | Secrets Manager secret name | `snowflake-credentials` |
| `API_TITLE` | API title | `FastAPI Snowflake API` |
| `API_VERSION` | API version | `1.0.0` |
| `DEBUG` | Debug mode | `false` |

### Terraform Variables

See `terraform/variables.tf` for all configurable options including:

- AWS region and resource naming
- Lambda function configuration (memory, timeout)
- API Gateway settings
- Snowflake credentials (sensitive)

## Security

- 🔐 All secrets stored in AWS Secrets Manager
- 🛡️ IAM roles with minimal required permissions
- 🔒 Input validation with Pydantic models
- 🌐 CORS configuration for web security
- 📝 Comprehensive logging for audit trails

## Monitoring and Logging

- CloudWatch Logs for Lambda function logs
- API Gateway access logging
- Custom metrics for monitoring application performance
- Health check endpoints for load balancer integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:

1. Check the [Issues](issues) page
2. Review the API documentation at `/docs` endpoint
3. Check CloudWatch logs for debugging

## Related Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Snowflake Python Connector](https://docs.snowflake.com/en/user-guide/python-connector.html)
- [AWS Lambda Python Runtime](https://docs.aws.amazon.com/lambda/latest/dg/python-programming-model.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
#   p y t h o n - s n o w f l a k e - a p i  
 