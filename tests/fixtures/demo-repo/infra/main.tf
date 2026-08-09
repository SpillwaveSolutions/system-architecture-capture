provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "prod" {
  cidr_block = "10.20.0.0/16"
}

resource "aws_iam_role" "order_service" {
  name = "order-service-role"
}
