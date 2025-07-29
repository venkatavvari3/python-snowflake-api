# Deployment Guide

This guide walks you through deploying the FastAPI Snowflake application to AWS.

## Prerequisites

1. **AWS CLI** configured with appropriate permissions
2. **Terraform** installed (version 1.0+)
3. **Python 3.11+** installed
4. **Snowflake account** with appropriate permissions

## Step 1: Prepare Environment

```bash
# Clone the repository and navigate to the project
cd python-snowflake-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Snowflake

1. Create a database and schema in Snowflake
2. Run the setup SQL script:
   ```sql
   -- See sql/setup.sql for complete setup
   CREATE OR REPLACE TABLE users (
       id INT AUTOINCREMENT PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       email VARCHAR(255) NOT NULL UNIQUE,
       created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
   );
   ```

## Step 3: Configure Terraform

```bash
cd terraform

# Copy the example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
# Make sure to update:
# - aws_region
# - snowflake_credentials (all fields)
# - project_name and environment if desired
```

## Step 4: Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Review the deployment plan
terraform plan

# Deploy the infrastructure
terraform apply
```

After deployment, Terraform will output:
- API Gateway URL
- Lambda function name
- CloudWatch log group name

## Step 5: Test the Deployment

```bash
# Test the health endpoint
curl https://your-api-url/health

# Test the database health endpoint
curl https://your-api-url/health/database

# Get users
curl https://your-api-url/users

# Create a new user
curl -X POST https://your-api-url/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

## Step 6: Monitor and Debug

### CloudWatch Logs
- Lambda logs: `/aws/lambda/your-function-name`
- API Gateway logs: (configured in API Gateway console)

### Common Issues

1. **Secrets Manager Access**: Ensure Lambda has permission to read secrets
2. **Snowflake Connectivity**: Check VPC configuration if using private Snowflake
3. **API Gateway Timeout**: Increase Lambda timeout for slow queries

## Cleanup

To remove all resources:

```bash
cd terraform
terraform destroy
```

## Security Considerations

- Never commit `terraform.tfvars` to version control
- Use least-privilege IAM policies
- Consider using VPC endpoints for Snowflake connections
- Enable CloudTrail for audit logging
- Rotate Snowflake credentials regularly

## Scaling and Performance

- Monitor Lambda concurrency and adjust reserved capacity
- Use Snowflake query optimization techniques
- Consider API Gateway caching for frequently accessed data
- Monitor CloudWatch metrics for performance bottlenecks
