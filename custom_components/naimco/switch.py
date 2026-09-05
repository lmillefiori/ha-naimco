"""Switch platform for the Naim Mu-so (NaimCo) integration."""

from __future__ import annotations

from typing import Any

from naimco import NaimCo

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import NaimcoEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Naim Mu-so cleaning mode switch entity."""
    device: NaimCo = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NaimcoCleaningMode(device, entry.entry_id)])


class NaimcoCleaningMode(NaimcoEntity, SwitchEntity):
    """Cleaning mode switch.

    Puts the unit in a state safe for wiping down its surfaces (disables
    touch controls) per the "Cleaning Mode" feature added upstream.
    """

    _attr_translation_key = "cleaning_mode"
    _attr_entity_registry_enabled_default = False

    def __init__(self, device: NaimCo, entry_id: str) -> None:
        """Initialize the cleaning mode switch entity."""
        super().__init__(device, entry_id, "cleaning_mode")

    @property
    def is_on(self) -> bool | None:
        return self._device.state.cleaningmode

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._device.set_cleaningmode(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._device.set_cleaningmode(False)
