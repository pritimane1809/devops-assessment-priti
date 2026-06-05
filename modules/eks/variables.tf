variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
}

variable "cluster_version" {
  description = "Kubernetes version."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for the EKS security group."
  type        = string
}

variable "subnet_ids" {
  description = "Subnets used by the EKS control plane."
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnets used by EKS managed node groups."
  type        = list(string)
}

variable "node_instance_types" {
  description = "Managed node group instance types."
  type        = list(string)
}

variable "node_desired_size" {
  description = "Desired node count."
  type        = number
}

variable "node_min_size" {
  description = "Minimum node count."
  type        = number
}

variable "node_max_size" {
  description = "Maximum node count."
  type        = number
}

variable "tags" {
  description = "Tags to apply to resources."
  type        = map(string)
  default     = {}
}

