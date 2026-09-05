"""Shared helpers for the Naim Mu-so (NaimCo) integration."""

from __future__ import annotations

import asyncio

from naimco import NaimCo

from homeassistant.exceptions import HomeAssistantError

from .const import CONNECT_TIMEOUT


async def wait_for_connection(device: NaimCo, timeout: float = CONNECT_TIMEOUT) -> None:
    """Wait until the device has an active connection.

    naimco's background connection task (started by startup()) resets
    device.controller back to None whenever the connection drops - e.g. when
    the unit goes into standby - and only sets it again once reconnected.
    Every command method needs a live controller, so callers should wait
    here first instead of hitting AttributeError: 'NoneType' object has no
    attribute 'nvm'.
    """
    elapsed = 0.0
    interval = 0.2
    while device.controller is None or device.controller.connection is None:
        if elapsed >= timeout:
            raise TimeoutError(f"Timed out connecting to {device.ip_address}")
        await asyncio.sleep(interval)
        elapsed += interval


async def async_ensure_connected(device: NaimCo, timeout: float = CONNECT_TIMEOUT) -> None:
    """Wait for the connection, raising a user-facing error if it times out."""
    try:
        await wait_for_connection(device, timeout)
    except TimeoutError as err:
        raise HomeAssistantError(
            "Naim Mu-so is not connected right now, try again in a moment"
        ) from err
