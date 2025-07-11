# Terraform module for aws-k8s-storage

This is a Terraform module facilitating the deployment of the aws-k8s-storage charm, using the [Terraform juju provider](https://github.com/juju/terraform-provider-juju/). For more information, refer to the provider [documentation](https://registry.terraform.io/providers/juju/juju/latest/docs).

## Requirements
This module requires a `juju` model to be available. Refer to the [usage section](#usage) below for more details.

## API

### Inputs
The module offers the following configurable inputs:

| Name | Type | Description | Required | Default |
| - | - | - | - | - |
| `app_name`| string | Application name | False | aws-k8s-storage |
| `base` | string | Ubuntu base to deploy the charm onto | False | ubuntu@22.04 |
| `channel`| string | Channel that the charm is deployed from | False | 1.31/stable |
| `config`| map(string) | Map of the charm configuration options | False | {} |
| `model`| string | Name of the model that the charm is deployed on | True | - |
| `revision`| number | Revision number of the charm name | False | null |

### Outputs
Upon applied, the module exports the following outputs:

| Name | Description |
| - | - |
| `app_name`| Application name |
| `requires`| Map of `requires` endpoints |

## Usage

This module is intended to be used as part of a higher-level module. When defining one, users should ensure that Terraform is aware of the `juju_model` dependency of the charm module. There are two options to do so when creating a high-level module:

### Define a `juju_model` resource
Define a `juju_model` resource and pass to the `model_name` input a reference to the `juju_model` resource's name. For example:

```
resource "juju_model" "testing" {
  name = canonical-k8s
}
module "aws_k8s_storage" {
  source = "git::https://github.com/charmed-kubernetes/aws-k8s-storage//terraform?ref=main"
  model = juju_model.testing.name
}
```

### Define a `data` source
Define a `data` source and pass to the `model_name` input a reference to the `data.juju_model` resource's name. This will enable Terraform to look for a `juju_model` resource with a name attribute equal to the one provided, and apply only if this is present. Otherwise, it will fail before applying anything.
```
data "juju_model" "testing" {
  name = var.model_name
}
module "aws_k8s_storage" {
  source = "git::https://github.com/charmed-kubernetes/aws-k8s-storage//terraform?ref=main"
  model = data.juju_model.testing.name
}
```
