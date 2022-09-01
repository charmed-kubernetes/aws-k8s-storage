# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
"""Config Management for the aws cloud provider charm."""

import logging
import subprocess
from typing import Mapping, Optional, TypedDict

import yaml
from pydantic import BaseModel, Field, SecretStr, ValidationError

log = logging.getLogger(__name__)


class Credentials(BaseModel):
    access_key: SecretStr = Field(alias="access-key", min_length=1)
    secret_key: SecretStr = Field(alias="secret-key", min_length=1)


class CredentialsError(Exception):
    pass


class CharmConfig:
    """Representation of the charm configuration."""

    def __init__(self, charm):
        """Creates a CharmConfig object from the configuration data."""
        self.config = charm.config

    @property
    def credentials(self) -> Credentials:
        """
        Get the credentials from either the config or the hook tool.

        Prefers the config so that it can be overridden.
        """
        try:
            result = subprocess.run(
                ["credential-get"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            creds = yaml.load(result.stdout.decode("utf8"))
            return Credentials(**creds["credential"]["attributes"])
        except ValidationError as e:
            no_creds_msg = "trust credentials invalid."
            raise CredentialsError(no_creds_msg) from e
        except FileNotFoundError:
            # juju trust not available
            no_creds_msg = "missing credentials; set via config"
        except subprocess.CalledProcessError as e:
            if "permission denied" not in e.stderr.decode("utf8"):
                raise
            no_creds_msg = "missing credentials access; grant with: juju trust"

        # try access-key and secret-key config
        try:
            return Credentials(**self.config)
        except ValidationError as e:
            raise CredentialsError(no_creds_msg) from e

    @property
    def available_data(self):
        """Parse valid charm config into a dict, drop keys if unset."""
        data = {}
        for key, value in self.config.items():
            if key in Credentials.schema()["required"]:
                continue
            data[key] = value

        for key, value in dict(**data).items():
            if value == "" or value is None:
                del data[key]

        return data

    def evaluate(self) -> Optional[str]:
        """Determine if configuration is valid."""
        try:
            self.credentials
        except CredentialsError as e:
            return str(e)
        return None
