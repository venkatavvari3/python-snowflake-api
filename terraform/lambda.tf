# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 14

  tags = {
    Name = "${var.project_name}-${var.environment}-lambda-logs"
  }
}

# Lambda function
resource "aws_lambda_function" "main" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.lambda_function_name}-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler.handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size

  environment {
    variables = {
      AWS_SECRET_NAME = aws_secretsmanager_secret.snowflake_credentials.name
      AWS_REGION     = var.aws_region
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy_attachment.lambda_secrets_policy,
    aws_cloudwatch_log_group.lambda_logs,
  ]

  tags = {
    Name = "${var.project_name}-${var.environment}-lambda"
  }
}

# Create deployment package
data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/lambda_deployment.zip"
  
  source {
    content = templatefile("${path.module}/../app/lambda_handler.py", {})
    filename = "app/lambda_handler.py"
  }
  
  source {
    content = templatefile("${path.module}/../app/main.py", {})
    filename = "app/main.py"
  }
  
  source {
    content = templatefile("${path.module}/../app/config.py", {})
    filename = "app/config.py"
  }
  
  source {
    content = templatefile("${path.module}/../app/database.py", {})
    filename = "app/database.py"
  }
  
  source {
    content = templatefile("${path.module}/../app/secrets.py", {})
    filename = "app/secrets.py"
  }
  
  source {
    content = templatefile("${path.module}/../app/models.py", {})
    filename = "app/models.py"
  }
  
  source {
    content = templatefile("${path.module}/../app/__init__.py", {})
    filename = "app/__init__.py"
  }
  
  source {
    content = templatefile("${path.module}/../requirements.txt", {})
    filename = "requirements.txt"
  }
}
