"""The Naim Mu-so (NaimCo) integration."""

from __future__ import annotations

import asyncio
import logging

from naimco import NaimCo

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import CONNECT_TIMEOUT, DOMAIN, PLATFORMS, SIGNAL_UPDATE

_LOGGER = logging.getLogger(__name__)


async def _wait_for_connection(device: NaimCo, timeout: float = CONNECT_TIMEOUT) -> None:
    """Wait until device.startup() has established a connection.

    naimco's startup() only schedules a background connection task and
    returns immediately, so device.controller stays None for a moment.
    Callers must wait for it before issuing any commands.
    """
    elapsed = 0.0
    interval = 0.2
    while device.controller is None or device.controller.connection is None:
        if elapsed >= timeout:
            raise TimeoutError(f"Timed out connecting to {device.ip_address}")
        await asyncio.sleep(interval)
        elapsed += interval


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Naim Mu-so from a config entry."""
    host = entry.data[CONF_HOST]

    async def _on_state_update(_state) -> None:
        async_dispatcher_send(hass, SIGNAL_UPDATE.format(entry_id=entry.entry_id))

    device = NaimCo(host, callback=_on_state_update)

    try:
        await device.startup()
        await _wait_for_connection(device)
    except (TimeoutError, OSError, ValueError) as err:
        raise ConfigEntryNotReady(f"Unable to connect to Mu-so at {host}") from err

    await device.update_data()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = device

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        device: NaimCo = hass.data[DOMAIN].pop(entry.entry_id)
        await device.shutdown()
    return unload_ok
