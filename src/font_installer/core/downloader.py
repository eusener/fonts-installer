"""File downloader with progress reporting."""

import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from ..config.settings import Settings
from .exceptions import DownloadError


@dataclass
class DownloadProgress:
    """Progress information for a download."""

    name: str
    percent: int
    status: str
    bytes_downloaded: int = 0
    total_bytes: int = 0


class ProgressCallback(Protocol):
    """Protocol for progress callback functions."""

    def __call__(self, progress: DownloadProgress) -> None: ...


class Downloader:
    """Handles file downloads with progress reporting."""

    def __init__(self, progress_callback: ProgressCallback | None = None):
        self._callback = progress_callback

    def _report(
        self,
        name: str,
        percent: int,
        status: str,
        downloaded: int = 0,
        total: int = 0,
    ) -> None:
        """Report progress to callback if set."""
        if self._callback:
            self._callback(
                DownloadProgress(
                    name=name,
                    percent=percent,
                    status=status,
                    bytes_downloaded=downloaded,
                    total_bytes=total,
                )
            )

    def download_file(self, url: str, dest: Path, name: str) -> Path:
        """
        Download a file from URL to destination path.

        Args:
            url: Source URL
            dest: Destination path
            name: Display name for progress

        Returns:
            Path to downloaded file

        Raises:
            DownloadError: If download fails
        """
        try:
            self._report(name, 0, "Iniciando download...")

            def progress_hook(block_num: int, block_size: int, total_size: int) -> None:
                if total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(100, downloaded * 100 // total_size)
                    self._report(name, percent, f"Baixando... {percent}%", downloaded, total_size)

            urllib.request.urlretrieve(url, dest, reporthook=progress_hook)
            self._report(name, 100, "Download concluido!")
            return dest

        except urllib.error.HTTPError as e:
            raise DownloadError(url, f"HTTP {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise DownloadError(url, str(e.reason))
        except Exception as e:
            raise DownloadError(url, str(e))

    def get_github_release_url(self, repo: str, asset_pattern: str) -> str | None:
        """
        Get download URL for latest GitHub release asset.

        Args:
            repo: GitHub repo in format "owner/repo"
            asset_pattern: Pattern to match asset filename

        Returns:
            Download URL or None if not found
        """
        api_url = f"{Settings.GITHUB_API_BASE}/{repo}/releases/latest"

        try:
            req = urllib.request.Request(api_url)
            req.add_header("User-Agent", Settings.USER_AGENT)

            with urllib.request.urlopen(req, timeout=Settings.API_TIMEOUT) as response:
                data = json.loads(response.read().decode())

            # First try to find exact pattern match
            for asset in data.get("assets", []):
                name = asset.get("name", "")
                if asset_pattern.lower() in name.lower() and name.endswith(".zip"):
                    return asset.get("browser_download_url")

            # Fallback: any zip file
            for asset in data.get("assets", []):
                if asset.get("name", "").endswith(".zip"):
                    return asset.get("browser_download_url")

        except Exception:
            pass

        return None
