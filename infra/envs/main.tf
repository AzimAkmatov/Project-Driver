terraform {
  required_version = ">= 1.6.0"
}

locals { env = "dev" }

# Later: call modules here (vpc, rds, ecs_service, cloudfront_s3, secrets)
output "env" { value = local.env }
