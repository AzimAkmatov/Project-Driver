terraform {
  backend "s3" {
    bucket         = "project-driver-terraform-state"
    key            = "envs/dev/terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "project-driver-tf-locks"
    encrypt        = true
  }
}
