
# terraform/variables.tf - Input variables

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev, prod)"
  type        = string
  default     = "dev"
}

variable "website_domain" {
  description = "Domain name for the resume website"
  type        = string
  default     = "lucas-albuquerque.com"
}

variable "website_name" {
  description = "Name used for resource naming"
  type        = string
  default     = "resume"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Project     = "Serverless-Resume"
    ManagedBy   = "Terraform"
    Owner       = "Lucas"
  }
}