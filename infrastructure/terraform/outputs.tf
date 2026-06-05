output "vpc_id" {
  description = "VPC ID created by CloudDrove VPC module."
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs."
  value       = values(aws_subnet.public)[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs."
  value       = values(aws_subnet.private)[*].id
}

output "cluster_name" {
  description = "EKS cluster name."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint."
  value       = module.eks.cluster_endpoint
}

output "frontend_ecr_repository_url" {
  description = "Frontend ECR repository URL."
  value       = aws_ecr_repository.frontend.repository_url
}

output "backend_ecr_repository_url" {
  description = "Backend ECR repository URL."
  value       = aws_ecr_repository.backend.repository_url
}
