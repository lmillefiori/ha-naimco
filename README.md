# Home Assistant integration for Naim Mu-so

A [Home Assistant](https://www.home-assistant.io/) custom integration for Naim Mu-so
all-in-one players, built on top of the [NaimCo](https://github.com/blitzkopf/NaimCo)
library.

## Entities

- **media_player** — power (standby), volume, mute, source select (radio/digital/
  Spotify/USB/UPnP/Tidal/front inputs), play/pause/stop/next/previous, now-playing
  title/artist/album/artwork. Radio presets are listed in the `presets` attribute and
  can be selected with the `media_player.play_media` service using
  `media_content_type: preset` and `media_content_id: "<preset number>"`.
- **light** ("Illumination", disabled by default) — front-panel illumination
  brightness. Naim doesn't document the valid range for this command; it's
  currently mapped as a 3-level (off/low/high) dimmer based on observed values —
  see `ILLUM_MAX` in `const.py` if your unit needs a different range.
- **switch** ("Cleaning mode", disabled by default) — puts the unit into cleaning
  mode (disables touch controls so you can wipe the case down).

## Installation

### HACS (custom repository)

1. HACS → Integrations → ⋮ → Custom repositories.
2. Add this repository URL with category "Integration".
3. Install "Naim Mu-so", then restart Home Assistant.

### Manual

Copy `custom_components/naimco` into your Home Assistant `config/custom_components/`
directory and restart Home Assistant.

## Setup

Settings → Devices & Services → Add Integration → "Naim Mu-so". Units on the same
network are auto-discovered via SSDP and will show up as a discovered device; you can
also add one manually by IP address.

## Known limitations

- Only tested against a single Mu-so unit; multi-room setups are untested.
- The illumination brightness range (`ILLUM_MAX`) is a best guess — Naim does not
  publish the valid `SETILLUM` range.
- The underlying [NaimCo](https://github.com/blitzkopf/NaimCo) protocol was reverse
  engineered from the Naim app, not from official documentation, so some fields
  or states may be incomplete.

## License

MIT, see [LICENSE](LICENSE).
