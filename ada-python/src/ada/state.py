"""State management for ADA.

Manages the ``~/.ada/`` directory used for persistent state:
- Channel metadata and event ID tracking
- Bulk request logging
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger("ada.state")


class AdaState:
    """Manages ~/.ada/ state directory."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_dir or Path.home() / ".ada")
        self.channels_dir = self.base_dir / "channels"
        self.requests_log = self.base_dir / "requests.log"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """Create state directories if they don't exist."""
        self.base_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.channels_dir.mkdir(mode=0o700, exist_ok=True)
        if not self.requests_log.exists():
            self.requests_log.touch(mode=0o600)

    # ---- Channel State ----

    def get_channel_name(self, channel_id: str) -> Optional[str]:
        """Get the human-readable name for a channel ID."""
        path = self.channels_dir / f"channel-name-{channel_id}"
        if path.exists():
            return path.read_text().strip()
        return None

    def save_channel_name(self, channel_id: str, name: str) -> None:
        """Save the mapping of channel ID to human-readable name."""
        path = self.channels_dir / f"channel-name-{channel_id}"
        path.write_text(name)

    def get_last_event_id(self, channel_id: str) -> Optional[str]:
        """Get the last processed event ID for a channel."""
        path = self.channels_dir / f"channel-status-{channel_id}"
        if path.exists():
            match = re.search(r"\d+", path.read_text())
            return match.group(0) if match else None
        return None

    def save_last_event_id(self, channel_id: str, event_id: str) -> None:
        """Save the last processed event ID for resume support."""
        path = self.channels_dir / f"channel-status-{channel_id}"
        path.write_text(event_id)

    def find_channel_id_by_name(self, name: str) -> Optional[str]:
        """Find a channel ID by its human-readable name."""
        for path in self.channels_dir.glob("channel-name-*"):
            if path.read_text().strip() == name:
                return path.name.replace("channel-name-", "")
        return None

    def delete_channel_files(self, channel_id: str) -> None:
        """Remove all state files for a channel."""
        for prefix in ("channel-name-", "channel-status-"):
            path = self.channels_dir / f"{prefix}{channel_id}"
            path.unlink(missing_ok=True)

    def list_channels(self) -> list[dict[str, str]]:
        """List all known channels with their IDs and names."""
        channels: list[dict[str, str]] = []
        for path in sorted(self.channels_dir.glob("channel-name-*")):
            channel_id = path.name.replace("channel-name-", "")
            name = path.read_text().strip()
            last_event = self.get_last_event_id(channel_id) or "none"
            channels.append({
                "id": channel_id,
                "name": name,
                "last_event_id": last_event,
            })
        return channels

    # ---- Request Logging ----

    def log_request(self, lines: list[str]) -> None:
        """Append lines to the requests log."""
        with self.requests_log.open("a") as f:
            for line in lines:
                f.write(line + "\n")
