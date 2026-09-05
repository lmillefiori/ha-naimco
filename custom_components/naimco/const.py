"""Constants for the Naim Mu-so (NaimCo) integration."""

from homeassistant.const import Platform

DOMAIN = "naimco"

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER, Platform.LIGHT, Platform.SWITCH]

# naimco.startup() only schedules the background connection task and returns
# immediately, so callers have to wait for the connection to actually be
# established before issuing commands. This is how long we wait before
# giving up.
CONNECT_TIMEOUT = 10

SIGNAL_UPDATE = f"{DOMAIN}_update_{{entry_id}}"

MANUFACTURER = "Naim Audio Ltd."

# SETILLUM/GETILLUM appear to accept a small integer range (observed values
# 0-2 in the wild: off / low / high). Not documented anywhere by Naim, so
# this is the best guess and may need adjusting if a unit reports otherwise.
ILLUM_MAX = 2
