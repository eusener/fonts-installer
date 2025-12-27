"""Font definitions and metadata."""

from dataclasses import dataclass
from enum import Enum


class FontCategory(Enum):
    """Font category enumeration."""

    CLEARTYPE = "cleartype"
    DEVELOPER = "developer"
    CORE = "core"


@dataclass(frozen=True)
class FontInfo:
    """Font metadata."""

    name: str
    description: str
    category: FontCategory
    repo: str | None = None  # GitHub repo for dev fonts
    asset_pattern: str | None = None  # Pattern to match release assets


# Microsoft ClearType Fonts (included in PowerPoint Viewer)
CLEARTYPE_FONTS: dict[str, FontInfo] = {
    "calibri": FontInfo(
        name="Calibri",
        description="Sans-serif moderna, padrao do Office",
        category=FontCategory.CLEARTYPE,
    ),
    "cambria": FontInfo(
        name="Cambria",
        description="Serif elegante para documentos",
        category=FontCategory.CLEARTYPE,
    ),
    "consolas": FontInfo(
        name="Consolas",
        description="Monospace para programacao",
        category=FontCategory.CLEARTYPE,
    ),
    "constantia": FontInfo(
        name="Constantia",
        description="Serif classica",
        category=FontCategory.CLEARTYPE,
    ),
    "corbel": FontInfo(
        name="Corbel",
        description="Sans-serif humanista",
        category=FontCategory.CLEARTYPE,
    ),
    "candara": FontInfo(
        name="Candara",
        description="Sans-serif suave",
        category=FontCategory.CLEARTYPE,
    ),
}


# Developer Fonts (from GitHub releases)
DEV_FONTS: dict[str, FontInfo] = {
    "cascadia": FontInfo(
        name="Cascadia Code",
        description="Fonte oficial do Windows Terminal",
        category=FontCategory.DEVELOPER,
        repo="microsoft/cascadia-code",
        asset_pattern="CascadiaCode",
    ),
    "jetbrains": FontInfo(
        name="JetBrains Mono",
        description="Fonte do JetBrains para IDEs",
        category=FontCategory.DEVELOPER,
        repo="JetBrains/JetBrainsMono",
        asset_pattern="JetBrainsMono",
    ),
    "firacode": FontInfo(
        name="Fira Code",
        description="Monospace com ligaduras",
        category=FontCategory.DEVELOPER,
        repo="tonsky/FiraCode",
        asset_pattern="Fira_Code",
    ),
    "hack": FontInfo(
        name="Hack",
        description="Fonte limpa para codigo",
        category=FontCategory.DEVELOPER,
        repo="source-foundry/Hack",
        asset_pattern="Hack-",
    ),
    "sourcecodepro": FontInfo(
        name="Source Code Pro",
        description="Fonte Adobe para programacao",
        category=FontCategory.DEVELOPER,
        repo="adobe-fonts/source-code-pro",
        asset_pattern="OTF",
    ),
    "victormono": FontInfo(
        name="Victor Mono",
        description="Italico cursivo elegante",
        category=FontCategory.DEVELOPER,
        repo="rubjo/victor-mono",
        asset_pattern="VictorMono",
    ),
    "inconsolata": FontInfo(
        name="Inconsolata",
        description="Monospace classica do Google",
        category=FontCategory.DEVELOPER,
        repo="googlefonts/Inconsolata",
        asset_pattern="fonts",
    ),
}


def get_all_fonts() -> dict[str, FontInfo]:
    """Get all available fonts."""
    return {**CLEARTYPE_FONTS, **DEV_FONTS}


def get_fonts_by_category(category: FontCategory) -> dict[str, FontInfo]:
    """Get fonts filtered by category."""
    all_fonts = get_all_fonts()
    return {k: v for k, v in all_fonts.items() if v.category == category}
