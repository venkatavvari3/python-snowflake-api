variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "fastapi-snowflake"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "fastapi-snowflake-api"
}

variable "lambda_runtime" {
  description = "Runtime for Lambda function"
  type        = string
  default     = "python3.11"
}

variable "lambda_timeout" {
  description = "Timeout for Lambda function in seconds"
  type        = number
  default     = 30
}

variable "lambda_memory_size" {
  description = "Memory size for Lambda function in MB"
  type        = number
  default     = 256
}

variable "api_gateway_stage" {
  description = "API Gateway stage name"
  type        = string
  default     = "prod"
}

variable "snowflake_credentials" {
  description = "Snowflake credentials to store in Secrets Manager"
  type = object({
    account   = string
    user      = string
    password  = string
    warehouse = string
    database  = string
    schema    = string
    role      = string
  })
  sensitive = true
  default = {
    account   = ""
    user      = ""
    password  = ""
    warehouse = ""
    database  = ""
    schema    = ""
    role      = ""
  }
}
