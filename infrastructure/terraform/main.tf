data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  azs         = slice(data.aws_availability_zones.available.names, 0, 2)

  public_subnet_cidrs  = ["10.40.1.0/24", "10.40.2.0/24"]
  private_subnet_cidrs = ["10.40.11.0/24", "10.40.12.0/24"]

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

module "vpc" {
  source = "git::https://github.com/clouddrove/terraform-aws-vpc.git?ref=1.3.1&depth=1"

  name        = var.project_name
  environment = var.environment
  label_order = ["name", "environment"]

  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
}

resource "aws_subnet" "public" {
  for_each = {
    for index, cidr in local.public_subnet_cidrs : index => cidr
  }

  vpc_id                  = module.vpc.vpc_id
  cidr_block              = each.value
  availability_zone       = local.azs[tonumber(each.key)]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name                                             = "${local.name_prefix}-public-${tonumber(each.key) + 1}"
    "kubernetes.io/role/elb"                         = "1"
    "kubernetes.io/cluster/${local.name_prefix}-eks" = "shared"
  })
}

resource "aws_subnet" "private" {
  for_each = {
    for index, cidr in local.private_subnet_cidrs : index => cidr
  }

  vpc_id            = module.vpc.vpc_id
  cidr_block        = each.value
  availability_zone = local.azs[tonumber(each.key)]

  tags = merge(local.common_tags, {
    Name                                             = "${local.name_prefix}-private-${tonumber(each.key) + 1}"
    "kubernetes.io/role/internal-elb"                = "1"
    "kubernetes.io/cluster/${local.name_prefix}-eks" = "shared"
  })
}

resource "aws_eip" "nat" {
  domain = "vpc"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-nat-eip"
  })
}

resource "aws_nat_gateway" "this" {
  allocation_id = aws_eip.nat.id
  subnet_id     = values(aws_subnet.public)[0].id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-nat"
  })

  depends_on = [module.vpc]
}

resource "aws_route_table" "public" {
  vpc_id = module.vpc.vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = module.vpc.igw_id
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-rt"
  })
}

resource "aws_route_table" "private" {
  vpc_id = module.vpc.vpc_id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.this.id
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-rt"
  })
}

resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private.id
}

resource "aws_ecr_repository" "frontend" {
  name                 = "${local.name_prefix}-frontend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.common_tags
}

resource "aws_ecr_repository" "backend" {
  name                 = "${local.name_prefix}-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.common_tags
}

module "eks" {
  source = "../../modules/eks"

  cluster_name        = "${local.name_prefix}-eks"
  cluster_version     = var.cluster_version
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = concat([for subnet in values(aws_subnet.public) : subnet.id], [for subnet in values(aws_subnet.private) : subnet.id])
  private_subnet_ids  = [for subnet in values(aws_subnet.private) : subnet.id]
  node_instance_types = var.node_instance_types
  node_desired_size   = var.node_desired_size
  node_min_size       = var.node_min_size
  node_max_size       = var.node_max_size
  tags                = local.common_tags
}
