# aws-cloud-provider

## Description

This subordinate charm manages the cloud-provider and ebs-csi-driver components in AWS.

## Usage

The charm requires aws credentials and connection information, which
can be provided either directly, via config, or via the `aws-integration`
relation to the [AWS Integrator charm](https://charmhub.io/aws-integrator).

## Deployment

### The full process

```bash
juju deploy charmed-kubernetes
juju deploy aws-integrator --trust
juju deploy aws-cloud-provider

juju relate aws-cloud-provider:certificates            easyrsa
juju relate aws-cloud-provider:kube-control            kubernetes-control-plane
juju relate aws-cloud-provider:external-cloud-provider kubernetes-control-plane
juju relate aws-cloud-provider                         aws-integrator

##  wait for the vsphere controller daemonset to be running
kubectl describe nodes |egrep "Taints:|Name:|Provider"
```

### Details

* Requires a `charmed-kubernetes` deployment on a aws cloud launched by juju
* Deploy the `aws-integrator` charm into the model using `--trust` so juju provided aws credentials
* Deploy the `aws-cloud-provider` charm in the model relating to the integrator and to charmed-kubernetes components
* Once the model is active/idle, the cloud-provider charm will have successfully deployed the aws controller in the kube-system namespace
* Taint the existing nodes so the controller will apply the correct provider id to those nodes.
* Confirm the `ProviderID` is set on each node

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines
on enhancements to this charm following best practice guidelines, and
[CONTRIBUTING.md](https://github.com/charmed-kubernetes/aws-cloud-provider/blob/main/CONTRIBUTING.md)
for developer guidance.
