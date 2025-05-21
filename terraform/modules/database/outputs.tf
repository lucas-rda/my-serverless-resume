# terraform/modules/database/outputs.tf

output "table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.visitors.name
}

output "table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.visitors.arn
}

output "table_id" {
  description = "ID of the DynamoDB table"
  value       = aws_dynamodb_table.visitors.id
}

output "gsi_name" {
  description = "Name of the Global Secondary Index"
  value       = "ip-timestamp-index"
}