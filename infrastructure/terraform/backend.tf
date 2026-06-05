terraform {
  backend "s3" {
    bucket         = "priti-devops-tfstate-2026"
    key            = "cloudmaven/dev/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "cloudmaven-terraform-locks"
    encrypt        = true

  }
}

