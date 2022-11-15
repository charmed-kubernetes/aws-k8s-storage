# aws-k8s-storage

## Description

This subordinate charm manages the ebs-csi-driver components in AWS.

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
juju deploy aws-k8s-storage

juju relate aws-k8s-storage:certificates     easyrsa:client
juju relate aws-k8s-storage:kube-control     kubernetes-control-plane:kube-control
juju relate aws-k8s-storage:aws-integration  aws-integrator:aws
juju relate kubernetes-control-plane:aws     aws-integrator:aws
juju relate kubernetes-worker:aws            aws-integrator:aws

##  wait for the kubernetes-control-plane to be active/idle
kubectl describe nodes |egrep "Taints:|Name:|Provider"
```

### Details

* Requires a `charmed-kubernetes` deployment on a aws cloud launched by juju
* Deploy the `aws-integrator` charm into the model using `--trust` so juju provided aws credentials
* Deploy the `aws-k8s-storage` charm in the model relating to the integrator and to charmed-kubernetes components
* Once the model is active/idle, the storage charm will have successfully deployed the aws ebs-csi in the `kube-system` namespace

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines
on enhancements to this charm following best practice guidelines, and
[CONTRIBUTING.md](https://github.com/charmed-kubernetes/aws-k8s-storage/blob/main/CONTRIBUTING.md)
for developer guidance.
