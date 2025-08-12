# Terraform outputs for AI Swagger Bot infrastructure

output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = "${aws_api_gateway_deployment.main.invoke_url}"
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.main.arn
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.main.function_name
}

output "lambda_function_invoke_arn" {
  description = "Lambda function invoke ARN"
  value       = aws_lambda_function.main.invoke_arn
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.main.endpoint
}

output "database_name" {
  description = "RDS database name"
  value       = aws_db_instance.main.db_name
}

output "database_port" {
  description = "RDS database port"
  value       = aws_db_instance.main.port
}

output "database_connection_string" {
  description = "RDS database connection string (without password)"
  value       = "postgresql://${aws_db_instance.main.username}@${aws_db_instance.main.endpoint}:${aws_db_instance.main.port}/${aws_db_instance.main.db_name}"
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
}

output "redis_port" {
  description = "ElastiCache Redis port"
  value       = aws_elasticache_cluster.main.cache_nodes[0].port
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnets
}

output "availability_zones" {
  description = "Availability zones"
  value       = module.vpc.azs
}

output "nat_gateway_ids" {
  description = "NAT Gateway IDs"
  value       = module.vpc.natgw_ids
}

output "cloudwatch_log_group_name" {
  description = "CloudWatch log group name for Lambda"
  value       = aws_cloudwatch_log_group.lambda.name
}

output "cloudwatch_log_group_arn" {
  description = "CloudWatch log group ARN for Lambda"
  value       = aws_cloudwatch_log_group.lambda.arn
}

output "lambda_security_group_id" {
  description = "Lambda security group ID"
  value       = aws_security_group.lambda.id
}

output "database_security_group_id" {
  description = "Database security group ID"
  value       = aws_security_group.database.id
}

output "redis_security_group_id" {
  description = "Redis security group ID"
  value       = aws_security_group.redis.id
}

output "lambda_role_arn" {
  description = "Lambda execution role ARN"
  value       = aws_iam_role.lambda_exec.arn
}

output "lambda_role_name" {
  description = "Lambda execution role name"
  value       = aws_iam_role.lambda_exec.name
}

output "api_gateway_rest_api_id" {
  description = "API Gateway REST API ID"
  value       = aws_api_gateway_rest_api.main.id
}

output "api_gateway_rest_api_name" {
  description = "API Gateway REST API name"
  value       = aws_api_gateway_rest_api.main.name
}

output "api_gateway_execution_arn" {
  description = "API Gateway execution ARN"
  value       = aws_api_gateway_rest_api.main.execution_arn
}

output "environment_info" {
  description = "Environment information"
  value = {
    environment     = var.environment
    aws_region     = var.aws_region
    project_name   = var.project_name
    deployment_time = timestamp()
  }
}

output "cost_estimation" {
  description = "Estimated monthly costs (approximate)"
  value = {
    lambda = {
      requests_per_month = 1000000
      estimated_cost    = "$1.20"
    }
    rds = {
      instance_class = var.database_instance_class
      storage_gb     = var.database_allocated_storage
      estimated_cost = var.environment == "prod" ? "$25.00" : "$15.00"
    }
    redis = {
      node_type      = var.redis_node_type
      estimated_cost = var.environment == "prod" ? "$15.00" : "$10.00"
    }
    api_gateway = {
      requests_per_month = 1000000
      estimated_cost    = "$3.50"
    }
    total_estimated_cost = var.environment == "prod" ? "$54.70" : "$39.70"
  }
}

output "monitoring_endpoints" {
  description = "Monitoring and health check endpoints"
  value = {
    health_check = "${aws_api_gateway_deployment.main.invoke_url}/health"
    api_docs     = "${aws_api_gateway_deployment.main.invoke_url}/docs"
    openapi_json = "${aws_api_gateway_deployment.main.invoke_url}/openapi.json"
  }
}

output "deployment_instructions" {
  description = "Deployment instructions"
  value = <<-EOT
    🚀 AI Swagger Bot розгорнуто успішно!
    
    📍 API Endpoint: ${aws_api_gateway_deployment.main.invoke_url}
    🔍 Health Check: ${aws_api_gateway_deployment.main.invoke_url}/health
    📚 API Docs: ${aws_api_gateway_deployment.main.invoke_url}/docs
    
    🔧 Для оновлення коду:
    1. Змініть код в src/ та api/ директоріях
    2. Запустіть: make quick-deploy ENVIRONMENT=${var.environment}
    
    📊 Для моніторингу:
    1. CloudWatch Logs: /aws/lambda/${aws_lambda_function.main.function_name}
    2. CloudWatch Metrics: AWS/Lambda, AWS/RDS, AWS/ElastiCache
    
    💰 Приблизна вартість: ${var.environment == "prod" ? "$54.70" : "$39.70"}/місяць
    
    🔐 Безпека:
    - VPC: ${module.vpc.vpc_id}
    - Database: ${aws_db_instance.main.endpoint}
    - Redis: ${aws_elasticache_cluster.main.cache_nodes[0].address}
    
    📞 Підтримка: README_SERVERLESS.md
  EOT
} 