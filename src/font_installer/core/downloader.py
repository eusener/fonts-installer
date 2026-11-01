"""Streaming downloads and additive progress events."""

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from http.client import HTTPException
from pathlib import Path
from typing import Protocol

from ..config.settings import Settings
from .exceptions import DownloadError, ProgressCallbackError


@dataclass
class DownloadProgress:
    name: str
    percent: int
    status: str
    bytes_downloaded: int = 0
    total_bytes: int = 0
    phase: str | None = None
    event: str | None = None


class ProgressCallback(Protocol):
    def __call__(self, progress: DownloadProgress) -> None: ...


def emit_progress(
    callback: ProgressCallback | None, progress: DownloadProgress
) -> None:
    """Preserve callback failures even when their cause is an OSError."""
    if callback is not None:
        try:
            callback(progress)
        except Exception as error:
            raise ProgressCallbackError("Falha no callback de progresso") from error


class Downloader:
    def __init__(self, progress_callback: ProgressCallback | None = None):
        self._callback = progress_callback

    def _report(self, name, percent, status, downloaded=0, total=0, event="progress"):
        emit_progress(
            self._callback,
            DownloadProgress(
                name, percent, status, downloaded, total, "download", event
            ),
        )

    def download_file(self, url: str, dest: Path, name: str) -> Path:
        self._report(name, 0, "Iniciando download", event="started")
        downloaded = total = 0
        try:
            with urllib.request.urlopen(
                url, timeout=Settings.DOWNLOAD_TIMEOUT
            ) as response:
                raw_total = response.headers.get("Content-Length", "0")
                total = int(raw_total) if raw_total.isdigit() else 0
                with dest.open("wb") as output:
                    while chunk := response.read(65536):
                        output.write(chunk)
                        downloaded += len(chunk)
                        percent = min(100, downloaded * 100 // total) if total else 0
                        self._report(name, percent, "Baixando", downloaded, total)
                if total and downloaded < total:
                    raise DownloadError(url, "Download incompleto")
        except (urllib.error.URLError, OSError, HTTPException) as error:
            raise DownloadError(url, str(error)) from error
        self._report(name, 100, "Download concluído", downloaded, total, "completed")
        return dest

    def get_github_release_url(self, repo: str, asset_pattern: str) -> str | None:
        url = f"{Settings.GITHUB_API_BASE}/{repo}/releases/latest"
        request = urllib.request.Request(
            url, headers={"User-Agent": Settings.USER_AGENT}
        )
        try:
            with urllib.request.urlopen(
                request, timeout=Settings.API_TIMEOUT
            ) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (
            urllib.error.URLError,
            OSError,
            HTTPException,
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as error:
            raise DownloadError(url, str(error)) from error
        if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
            raise DownloadError(url, "Resposta de release inválida")
        assets = data["assets"]
        for asset in assets:
            if (
                not isinstance(asset, dict)
                or not isinstance(asset.get("name"), str)
                or not isinstance(asset.get("browser_download_url"), str)
            ):
                raise DownloadError(url, "Asset de release inválido")
        zips = [asset for asset in assets if asset["name"].endswith(".zip")]
        for asset in zips:
            if asset_pattern.lower() in asset["name"].lower():
                return asset["browser_download_url"]
        return zips[0]["browser_download_url"] if zips else None
