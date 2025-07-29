# Secrets Manager for Snowflake credentials
resource "aws_secretsmanager_secret" "snowflake_credentials" {
  name                    = "${var.project_name}-${var.environment}-snowflake-credentials"
  description             = "Snowflake database credentials"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.project_name}-${var.environment}-snowflake-credentials"
  }
}

resource "aws_secretsmanager_secret_version" "snowflake_credentials" {
  secret_id = aws_secretsmanager_secret.snowflake_credentials.id
  secret_string = jsonencode({
    account   = var.snowflake_credentials.account
    user      = var.snowflake_credentials.user
    password  = var.snowflake_credentials.password
    warehouse = var.snowflake_credentials.warehouse
    database  = var.snowflake_credentials.database
    schema    = var.snowflake_credentials.schema
    role      = var.snowflake_credentials.role
  })
}
