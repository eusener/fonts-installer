"""Custom exceptions for font installer."""


class FontInstallerError(Exception):
    """Base exception for font installer."""

    def __init__(self, message: str, details: str | None = None):
        self.message = message
        self.details = details
        super().__init__(message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class DownloadError(FontInstallerError):
    """Error during file download."""

    def __init__(self, url: str, reason: str):
        super().__init__(
            message=f"Falha no download",
            details=f"{url} - {reason}",
        )
        self.url = url
        self.reason = reason


class ExtractionError(FontInstallerError):
    """Error during font extraction."""

    def __init__(self, file_path: str, reason: str):
        super().__init__(
            message="Falha na extracao",
            details=f"{file_path} - {reason}",
        )
        self.file_path = file_path
        self.reason = reason


class InstallationError(FontInstallerError):
    """Error during font installation."""

    def __init__(self, font_name: str, reason: str):
        super().__init__(
            message=f"Falha ao instalar {font_name}",
            details=reason,
        )
        self.font_name = font_name
        self.reason = reason


class DependencyError(FontInstallerError):
    """Missing system dependency."""

    def __init__(self, missing_tools: list[str]):
        tools_str = ", ".join(missing_tools)
        super().__init__(
            message="Dependencias faltando",
            details=f"Instale: sudo apt install {tools_str}",
        )
        self.missing_tools = missing_tools
