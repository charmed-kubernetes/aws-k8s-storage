# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_name" {
  description = "Name of the deployed application."
  value       = juju_application.aws_k8s_storage.name
}

output "requires" {
  value = {
    aws_integration = "aws-integration"
    kube_control = "kube-control"
    certificates = "certificates"

  }
}
