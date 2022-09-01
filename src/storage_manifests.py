# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
"""Implementation of aws specific details of the kubernetes manifests."""
import base64
import logging
import pickle
from hashlib import md5
from typing import Dict, Optional

from lightkube.codecs import AnyResource, from_dict
from ops.manifests import Addition, ConfigRegistry, ManifestLabel, Manifests

log = logging.getLogger(__file__)
SECRET_NAME = "aws-secret"
STORAGE_CLASS_NAME = "csi-aws-ebs-{type}"


class CreateSecret(Addition):
    """Create secret for the deployment."""

    CONFIG_TO_SECRET = {
        "access_key": "key_id",
        "secret_key": "access_key",
    }

    def __call__(self) -> Optional[AnyResource]:
        """Craft the secrets object for the deployment."""
        secret_config = {
            new_k: self.manifests.config.get(k) for k, new_k in self.CONFIG_TO_SECRET.items()
        }
        if any(s is None for s in secret_config.values()):
            log.error("secret data item is None")
            return None

        log.info("Encode secret data for storage.")
        for key, value in secret_config.items():
            value = value.encode("utf-8")
            secret_config[key] = base64.b64encode(value).decode("utf-8")

        return from_dict(
            dict(
                apiVersion="v1",
                kind="Secret",
                type="Opaque",
                metadata=dict(name=SECRET_NAME, namespace="kube-system"),
                data=secret_config,
            )
        )


class CreateStorageClass(Addition):
    """Create vmware storage class."""

    def __init__(self, manifests: "Manifests", sc_type: str):
        super().__init__(manifests)
        self.type = sc_type

    def __call__(self) -> Optional[AnyResource]:
        """Craft the storage class object."""
        storage_name = STORAGE_CLASS_NAME.format(type=self.type)
        log.info(f"Creating storage class {storage_name}")
        return from_dict(
            dict(
                apiVersion="storage.k8s.io/v1",
                kind="StorageClass",
                metadata=dict(
                    name=storage_name,
                ),
                provisioner="ebs.csi.aws.com",
                volumeBindingMode="WaitForFirstConsumer",
            )
        )


class AWSStorageManifests(Manifests):
    """Deployment Specific details for the aws-ebs-csi-driver."""

    def __init__(self, charm, charm_config, kube_control):
        super().__init__(
            "aws-ebs-csi-driver",
            charm.model,
            "upstream/cloud_storage",
            [
                CreateSecret(self),
                ManifestLabel(self),
                ConfigRegistry(self),
                CreateStorageClass(self, "default"),  # creates csi-aws-ebs-driver
            ],
        )
        self.charm_config = charm_config
        self.kube_control = kube_control

    @property
    def config(self) -> Dict:
        """Returns current config available from charm config and joined relations."""
        config: Dict = {}

        if self.kube_control.is_ready:
            config["image-registry"] = self.kube_control.get_registry_location()

        config.update(**self.charm_config.available_data)
        config.update(**{k: v.get_secret_value() for k, v in self.charm_config.credentials})

        for key, value in dict(**config).items():
            if value == "" or value is None:
                del config[key]

        config["release"] = config.pop("storage-release", None)
        return config

    def hash(self) -> int:
        """Calculate a hash of the current configuration."""
        return int(md5(pickle.dumps(self.config)).hexdigest(), 16)

    def evaluate(self) -> Optional[str]:
        """Determine if manifest_config can be applied to manifests."""
        props = CreateSecret.CONFIG_TO_SECRET.keys()
        for prop in props:
            value = self.config.get(prop)
            if not value:
                return f"Storage manifests waiting for definition of {prop}"
        return None
