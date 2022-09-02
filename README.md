# aws-cloud-provider

## Description

This subordinate charm manages the cloud-provider and ebs-csi-driver components in AWS.

## Prerequisites

It's important to understand that the control-plane and worker nodes will need
access to AWS credentials to facilitate features like creating loadbalancers, 
mounting volumes, and the like. AWS recommends accomplishing this by giving
each instance a set number of [policies](https://cloud-provider-aws.sigs.k8s.io/prerequisites/).

Use this policies to create instance-profiles which juju can use as constraints
for the worker and control-plane nodes.  See [juju instance-profiles](https://discourse.charmhub.io/t/using-aws-instance-profiles-with-juju-2-9/5185).


### Steps
1) use the IAM Policy/Role creator to create the two required instance-profiles
  * see [AWS: Using instance profiles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2_instance-profiles.html) for more information
2) Update the overlay used to deploy the bundle such that the applications use those instance-profiles
  * For example, if the instance-profile for the controller is named `ControlPlaneRole`, 

  ```yaml
  applications:
    kubernetes-control-plane:
      constraints: "cores=2 mem=8G root-disk=16G instance-role=ControlPlaneRole"
  ```


## Usage

The charm requires aws credentials and connection information, which
can be provided either directly, via config, or via the `aws-integration`
relation to the [AWS Integrator charm](https://charmhub.io/aws-integrator).

## Deployment

### The full process

```bash
juju deploy charmed-kubernetes
juju config kubernetes-control-plane allow-privileged=true
juju deploy aws-integrator --trust
juju deploy aws-cloud-provider --trust

juju relate aws-cloud-provider:certificates     easyrsa
juju relate aws-cloud-provider:kube-control     kubernetes-control-plane
juju relate aws-cloud-provider                  aws-integrator:clients
juju relate kubernetes-control-plane            aws-integrator:clients
juju relate kubernetes-worker                   aws-integrator:clients

##  wait for the kubernetes-control-plane to be active/idle
kubectl describe nodes |egrep "Taints:|Name:|Provider"
```

### Details

* Requires a `charmed-kubernetes` deployment on a aws cloud launched by juju
* Deploy the `aws-integrator` charm into the model using `--trust` so juju provided aws credentials
* Deploy the `aws-cloud-provider` charm in the model relating to the integrator and to charmed-kubernetes components
* Once the model is active/idle, the cloud-provider charm will have successfully deployed the aws ebs-csi in the kube-system namespace

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines
on enhancements to this charm following best practice guidelines, and
[CONTRIBUTING.md](https://github.com/charmed-kubernetes/aws-cloud-provider/blob/main/CONTRIBUTING.md)
for developer guidance.
