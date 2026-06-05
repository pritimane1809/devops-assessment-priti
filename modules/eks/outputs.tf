output "cluster_name" {
  description = "EKS cluster name."
  value       = aws_eks_cluster.this.name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint."
  value       = aws_eks_cluster.this.endpoint
}

output "cluster_security_group_id" {
  description = "EKS cluster security group ID."
  value       = aws_security_group.cluster.id
}

output "node_role_arn" {
  description = "EKS managed node group role ARN."
  value       = aws_iam_role.node.arn
}

