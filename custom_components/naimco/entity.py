"""Base entity for the Naim Mu-so (NaimCo) integration."""

from __future__ import annotations

from naimco import NaimCo

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, MANUFACTURER, SIGNAL_UPDATE


class NaimcoEntity(Entity):
    """Base class sharing device info and push updates across platforms."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, device: NaimCo, entry_id: str, unique_id_suffix: str) -> None:
        """Set up shared unique_id and device registry info."""
        self._device = device
        self._entry_id = entry_id
        device_id = device.serialnum or device.ip_address
        self._attr_unique_id = f"{device_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            manufacturer=MANUFACTURER,
            model=device.product or "Mu-so",
            name=device.roomname or device.ip_address,
        )

    async def async_added_to_hass(self) -> None:
        """Register for push updates from the device."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_UPDATE.format(entry_id=self._entry_id),
                self.async_write_ha_state,
            )
        )
