# terraform/modules/database/main.tf - DynamoDB module

# DynamoDB table for visitor tracking
resource "aws_dynamodb_table" "visitors" {
  name           = var.table_name
  billing_mode   = var.billing_mode
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }
  
  attribute {
    name = "ip"
    type = "S"
  }
  
  attribute {
    name = "timestamp"
    type = "N"
  }
  
  # Global Secondary Index for sorting by timestamp
  global_secondary_index {
    name               = "ip-timestamp-index"
    hash_key           = "ip"
    range_key          = "timestamp"
    projection_type    = "ALL"
    read_capacity      = var.billing_mode == "PROVISIONED" ? var.read_capacity : null
    write_capacity     = var.billing_mode == "PROVISIONED" ? var.write_capacity : null
  }
  
  tags = var.tags
}