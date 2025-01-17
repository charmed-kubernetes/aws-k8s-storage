# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "aws_k8s_storage" {
  name  = var.app_name
  model = var.model

  charm {
    name     = "aws-k8s-storage"
    channel  = var.channel
    revision = var.revision
    base     = var.base
  }

  config      = var.config
  constraints = var.constraints
}
