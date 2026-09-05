"""Config flow for the Naim Mu-so (NaimCo) integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import urlparse

import voluptuous as vol
from naimco import NaimCo

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.service_info.ssdp import (
    ATTR_UPNP_FRIENDLY_NAME,
    ATTR_UPNP_SERIAL,
    SsdpServiceInfo,
)

from .const import DOMAIN
from .util import wait_for_connection

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


class CannotConnect(Exception):
    """Error raised when we cannot connect to the Mu-so."""


async def _async_probe_device(host: str) -> dict[str, Any]:
    """Connect to a Mu-so and return identifying info, or raise CannotConnect."""
    device = NaimCo(host)
    try:
        await device.startup()
        await wait_for_connection(device, timeout=5)
        await device.update_data()
        # Give the initial NVM queries (roomname, serial number, ...) a moment
        # to come back before reading them.
        await asyncio.sleep(1)
        return {
            "serialnum": device.serialnum,
            "roomname": device.roomname,
        }
    except (TimeoutError, OSError, ValueError) as err:
        raise CannotConnect from err
    finally:
        await device.shutdown()


class NaimcoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Naim Mu-so."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_host: str | None = None
        self._discovered_name: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            try:
                info = await _async_probe_device(host)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                unique_id = info["serialnum"] or host
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(
                    title=info["roomname"] or "Naim Mu-so",
                    data={CONF_HOST: host},
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    async def async_step_ssdp(
        self, discovery_info: SsdpServiceInfo
    ) -> ConfigFlowResult:
        """Handle a discovered Mu-so."""
        host = urlparse(discovery_info.ssdp_location).hostname
        if host is None:
            return self.async_abort(reason="cannot_connect")

        serial = discovery_info.upnp.get(ATTR_UPNP_SERIAL)
        await self.async_set_unique_id(serial or host)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        self._discovered_host = host
        self._discovered_name = discovery_info.upnp.get(ATTR_UPNP_FRIENDLY_NAME)

        self.context["title_placeholders"] = {
            "name": self._discovered_name or host
        }
        return await self.async_step_ssdp_confirm()

    async def async_step_ssdp_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm a discovered Mu-so before adding it."""
        assert self._discovered_host is not None

        if user_input is not None:
            try:
                info = await _async_probe_device(self._discovered_host)
            except CannotConnect:
                return self.async_abort(reason="cannot_connect")
            return self.async_create_entry(
                title=info["roomname"] or self._discovered_name or "Naim Mu-so",
                data={CONF_HOST: self._discovered_host},
            )

        return self.async_show_form(
            step_id="ssdp_confirm",
            description_placeholders={
                "name": self._discovered_name or self._discovered_host
            },
        )
