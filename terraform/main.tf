
# terraform/main.tf - Main configuration file for Resume Website

# Call modules to create resources
module "s3_cloudfront" {
  source = "./modules/s3"

  website_domain      = var.website_domain
  website_name        = var.website_name
  environment         = var.environment
  tags                = var.tags
}

module "dynamodb" {
  source = "./modules/database"

  table_name          = "${var.website_name}-visitors-${var.environment}"
  billing_mode        = "PAY_PER_REQUEST"
  tags                = var.tags
}

module "api_lambda" {
  source = "./modules/api"

  api_name            = "${var.website_name}-api-${var.environment}"
  environment         = var.environment
  dynamodb_table_name = module.dynamodb.table_name
  dynamodb_table_arn  = module.dynamodb.table_arn
  website_domain      = var.website_domain
  tags                = var.tags
}

# Outputs from all modules are re-exported in outputs.tf