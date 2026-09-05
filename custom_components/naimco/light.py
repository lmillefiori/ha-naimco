"""Light platform for the Naim Mu-so (NaimCo) integration.

Controls the unit's front-panel illumination via SETILLUM/GETILLUM. Naim
does not document the valid range for this command; ILLUM_MAX in const.py
reflects the values observed in practice (0=off .. 2=brightest) and may need
adjusting for other Mu-so models/firmware.
"""

from __future__ import annotations

from typing import Any

from naimco import NaimCo

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ILLUM_MAX
from .entity import NaimcoEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Naim Mu-so illumination light entity."""
    device: NaimCo = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NaimcoIllumination(device, entry.entry_id)])


class NaimcoIllumination(NaimcoEntity, LightEntity):
    """Front-panel illumination brightness control."""

    _attr_translation_key = "illumination"
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_entity_registry_enabled_default = False

    def __init__(self, device: NaimCo, entry_id: str) -> None:
        """Initialize the illumination light entity."""
        super().__init__(device, entry_id, "illumination")

    @property
    def is_on(self) -> bool | None:
        illum = self._device.state.illum
        return illum is not None and illum > 0

    @property
    def brightness(self) -> int | None:
        illum = self._device.state.illum
        if illum is None:
            return None
        return round(illum / ILLUM_MAX * 255)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_ensure_connected()
        if ATTR_BRIGHTNESS in kwargs:
            level = round(kwargs[ATTR_BRIGHTNESS] / 255 * ILLUM_MAX)
            level = max(1, level)
        else:
            level = self._device.state.illum or ILLUM_MAX
        await self._device.set_illum(level)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_ensure_connected()
        await self._device.set_illum(0)
