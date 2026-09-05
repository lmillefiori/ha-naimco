"""Media player platform for the Naim Mu-so (NaimCo) integration."""

from __future__ import annotations

import logging
from typing import Any

from naimco import NaimCo

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import NaimcoEntity

_LOGGER = logging.getLogger(__name__)

_VIEWSTATE_PLAYING = {"PLAYING"}
_VIEWSTATE_PAUSED = {"PLAYERPAUSED", "PAUSED"}
_VIEWSTATE_STOPPED = {"PLAYERSTOPPED", "STOPPED"}

_FEATURES = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.PLAY_MEDIA
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Naim Mu-so media_player entity."""
    device: NaimCo = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NaimcoMediaPlayer(device, entry.entry_id)])


class NaimcoMediaPlayer(NaimcoEntity, MediaPlayerEntity):
    """Representation of a Naim Mu-so as a media player."""

    _attr_name = None
    _attr_supported_features = _FEATURES

    def __init__(self, device: NaimCo, entry_id: str) -> None:
        """Initialize the media player entity."""
        super().__init__(device, entry_id, "media_player")

    @property
    def state(self) -> MediaPlayerState:
        """Return the playback/power state, standby taking priority."""
        standby = self._device.standbystatus
        if standby and standby.get("state") == "ON":
            return MediaPlayerState.OFF

        viewstate = self._device.viewstate
        view_state = viewstate.get("state") if viewstate else None
        if view_state in _VIEWSTATE_PLAYING:
            return MediaPlayerState.PLAYING
        if view_state in _VIEWSTATE_PAUSED:
            return MediaPlayerState.PAUSED
        if view_state in _VIEWSTATE_STOPPED:
            return MediaPlayerState.IDLE
        return MediaPlayerState.ON

    @property
    def volume_level(self) -> float | None:
        """Volume level as 0..1, converted from the device's 0..100 range."""
        volume = self._device.volume
        return int(volume) / 100 if volume is not None else None

    @property
    def is_volume_muted(self) -> bool:
        return self._device.is_muted

    @property
    def source_list(self) -> list[str]:
        return list(self._device.inputs.values())

    @property
    def source(self) -> str | None:
        current = self._device.input
        return self._device.inputs.get(current, current)

    @property
    def media_title(self) -> str | None:
        return self._device.media_title

    @property
    def media_artist(self) -> str | None:
        return self._device.media_artist

    @property
    def media_album_name(self) -> str | None:
        return self._device.media_album_name

    @property
    def media_duration(self) -> int | None:
        duration = self._device.media_duration
        return int(duration) if duration is not None else None

    @property
    def media_image_url(self) -> str | None:
        return self._device.media_image_url

    @property
    def media_image_remotely_accessible(self) -> bool:
        return self._device.media_image_remotely_accessible

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose radio presets, selectable via play_media(media_type='preset', ...)."""
        return {"presets": self._device.presets}

    async def async_turn_on(self) -> None:
        await self._async_ensure_connected()
        await self._device.on()
        await self._async_refresh()

    async def async_turn_off(self) -> None:
        await self._async_ensure_connected()
        await self._device.off()
        await self._async_refresh()

    async def async_set_volume_level(self, volume: float) -> None:
        await self._async_ensure_connected()
        await self._device.set_volume(round(volume * 100))
        await self._async_refresh()

    async def async_volume_up(self) -> None:
        await self._async_ensure_connected()
        await self._device.volume_up()
        await self._async_refresh()

    async def async_volume_down(self) -> None:
        await self._async_ensure_connected()
        await self._device.volume_down()
        await self._async_refresh()

    async def async_mute_volume(self, mute: bool) -> None:
        await self._async_ensure_connected()
        await self._device.mute(mute)
        await self._async_refresh()

    async def async_media_play(self) -> None:
        await self._async_ensure_connected()
        await self._device.play()
        await self._async_refresh()

    async def async_media_pause(self) -> None:
        await self._async_ensure_connected()
        await self._device.pause()
        await self._async_refresh()

    async def async_media_stop(self) -> None:
        await self._async_ensure_connected()
        await self._device.stop()
        await self._async_refresh()

    async def async_media_next_track(self) -> None:
        await self._async_ensure_connected()
        await self._device.nexttrack()
        await self._async_refresh()

    async def async_media_previous_track(self) -> None:
        await self._async_ensure_connected()
        await self._device.prevtrack()
        await self._async_refresh()

    async def async_select_source(self, source: str) -> None:
        for input_id, name in self._device.inputs.items():
            if name == source:
                await self._async_ensure_connected()
                await self._device.select_input(input_id)
                await self._async_refresh()
                return
        _LOGGER.warning("Unknown source %s", source)

    async def async_play_media(
        self, media_type: str, media_id: str, **kwargs: Any
    ) -> None:
        """Select a radio preset via media_type='preset', media_id='<preset number>'."""
        if media_type == "preset":
            await self._async_ensure_connected()
            await self._device.select_preset(int(media_id))
            await self._async_refresh()
        else:
            _LOGGER.warning("Unsupported media type %s", media_type)
