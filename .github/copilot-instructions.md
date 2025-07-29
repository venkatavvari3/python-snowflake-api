<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# FastAPI Snowflake API Copilot Instructions

This is a Python FastAPI application with Snowflake database integration, designed for AWS Lambda deployment with Terraform infrastructure as code.

## Project Structure
- `app/`: FastAPI application code
- `tests/`: Pytest test suites
- `terraform/`: Infrastructure as code
- `scripts/`: Build and deployment scripts

## Key Technologies
- **FastAPI**: Modern, fast web framework for building APIs
- **Snowflake**: Cloud data platform for database operations
- **AWS Lambda**: Serverless compute for API deployment
- **AWS Secrets Manager**: Secure credential storage
- **Terraform**: Infrastructure as code
- **Pytest**: Testing framework

## Development Guidelines
1. Follow FastAPI best practices for async/await patterns
2. Use Pydantic models for data validation
3. Implement proper error handling with HTTP status codes
4. Use AWS Secrets Manager for all sensitive credentials
5. Write comprehensive tests with mocking for external dependencies
6. Use type hints throughout the codebase
7. Follow PEP 8 style guidelines

## Database Patterns
- Use context managers for database connections
- Implement connection pooling when needed
- Use parameterized queries to prevent SQL injection
- Handle Snowflake-specific data types appropriately

## AWS Lambda Considerations
- Keep cold start times minimal
- Use environment variables for configuration
- Implement proper logging with CloudWatch
- Handle timeouts and memory limits appropriately

## Testing Strategy
- Unit tests for individual components
- Integration tests for database operations
- Mock external dependencies (AWS services, Snowflake)
- Maintain high test coverage (80%+)

## Security Best Practices
- Never commit secrets to version control
- Use IAM roles with minimal required permissions
- Validate all input data with Pydantic
- Implement proper CORS configuration
- Use HTTPS in production
