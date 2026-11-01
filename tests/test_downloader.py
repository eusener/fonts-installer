"""Download contracts with in-memory HTTP responses, never the network."""

import io
import json

import pytest

from font_installer.core.downloader import Downloader, DownloadProgress
from font_installer.core.exceptions import DownloadError


class Response(io.BytesIO):
    def __init__(self, data, length=None):
        super().__init__(data)
        self.headers = {} if length is None else {"Content-Length": str(length)}


def test_additive_progress_contract():
    p = DownloadProgress("Font", 0, "waiting")
    assert p.phase is None and p.event is None


@pytest.mark.parametrize("length", [None, 5])
def test_streaming_reports_bytes_and_phases(monkeypatch, tmp_path, length):
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda *a, **kw: Response(b"hello", length)
    )
    events = []
    path = tmp_path / "font.zip"
    assert (
        Downloader(events.append).download_file(
            "https://example.test/font", path, "Font"
        )
        == path
    )
    assert path.read_bytes() == b"hello"
    assert events[0].phase == "download" and events[0].event == "started"
    assert events[-1].event == "completed"
    assert events[-1].bytes_downloaded == 5
    assert events[-1].total_bytes == (length or 0)


def test_callback_failure_is_not_download_error(monkeypatch, tmp_path):
    from font_installer.core.exceptions import ProgressCallbackError

    monkeypatch.setattr(
        "urllib.request.urlopen", lambda *a, **kw: Response(b"hello", 5)
    )

    def broken(_):
        raise OSError("callback bug")

    with pytest.raises(ProgressCallbackError) as error:
        Downloader(broken).download_file(
            "https://example.test/font", tmp_path / "font", "Font"
        )
    assert isinstance(error.value.__cause__, OSError)


@pytest.mark.parametrize("data", [b"not json", b"[]", b'{"assets":false}'])
def test_release_malformed_is_operational_error(monkeypatch, data):
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: Response(data))
    with pytest.raises(DownloadError):
        Downloader().get_github_release_url("owner/repo", "font")


def test_release_without_asset_is_none(monkeypatch):
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *a, **kw: Response(json.dumps({"assets": []}).encode()),
    )
    assert Downloader().get_github_release_url("owner/repo", "font") is None


def test_unexpected_network_adapter_error_propagates(monkeypatch, tmp_path):
    def broken(*a, **kw):
        raise TypeError("bug")

    monkeypatch.setattr("urllib.request.urlopen", broken)
    with pytest.raises(TypeError):
        Downloader().download_file(
            "https://example.test/font", tmp_path / "font", "Font"
        )


@pytest.mark.parametrize("operation", ["download", "release"])
def test_interrupted_http_body_is_operational_failure(monkeypatch, tmp_path, operation):
    from http.client import IncompleteRead

    class Interrupted(Response):
        def read(self, *args):
            raise IncompleteRead(b"partial")

    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: Interrupted(b""))
    with pytest.raises(DownloadError):
        if operation == "download":
            Downloader().download_file(
                "https://example.test", tmp_path / "font", "Font"
            )
        else:
            Downloader().get_github_release_url("owner/repo", "font")
