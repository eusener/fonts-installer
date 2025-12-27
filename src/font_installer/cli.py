"""Command-line interface for font installer."""

import sys

from .core.installer import FontInstaller
from .ui.app import FontInstallerApp
from .utils.system import SystemChecker


def print_help() -> None:
    """Print help message."""
    print(
        """
Font Installer para Ubuntu

Uso: font-installer [comando]

Comandos:
  (sem argumentos)  Abre interface interativa (TUI)
  --cli             Modo linha de comando (instala ClearType)
  --install-deps    Instala dependencias do sistema (cabextract, fontconfig)
  list              Lista fontes instaladas
  help, --help, -h  Mostra esta ajuda

Interface Interativa:
  Use Tab para navegar entre elementos
  Espaco para marcar/desmarcar checkboxes
  Enter para ativar botoes

Atalhos:
  a - Selecionar todas as fontes
  c - Limpar selecao
  i - Instalar selecionadas
  q - Sair

Nota: Este programa foi desenvolvido para Ubuntu/Debian.
"""
    )


def check_and_install_deps() -> bool:
    """
    Check dependencies and offer to install if missing.

    Returns:
        True if dependencies are available, False otherwise
    """
    ok, missing = FontInstaller.check_dependencies()

    if ok:
        return True

    print(f"Dependencias faltando: {', '.join(missing)}")
    print()

    # Ask user if they want to install
    try:
        response = input("Deseja instalar automaticamente? [S/n] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False

    if response in ("", "s", "sim", "y", "yes"):
        print("\nInstalando dependencias...")
        success, message = FontInstaller.install_dependencies()
        print(message)
        return success
    else:
        print("\nInstale manualmente com:")
        print("  sudo apt update && sudo apt install cabextract fontconfig")
        return False


def install_deps_command() -> int:
    """Install system dependencies."""
    print("Font Installer - Instalando Dependencias")
    print("-" * 40)

    ok, missing = FontInstaller.check_dependencies()

    if ok:
        print("Todas as dependencias ja estao instaladas!")
        return 0

    print(f"Instalando: {', '.join(missing)}")
    success, message = FontInstaller.install_dependencies()
    print(message)

    return 0 if success else 1


def run_cli_mode() -> int:
    """Run in CLI mode (non-interactive)."""
    print("Font Installer para Ubuntu - Modo CLI")
    print("-" * 40)

    # Check and install dependencies
    if not check_and_install_deps():
        return 1

    installer = FontInstaller(
        progress_callback=lambda p: print(f"  {p.name}: {p.status}")
    )

    print("\nInstalando fontes ClearType...")
    result = installer.install_cleartype_fonts()

    if result.success:
        print(f"\nSucesso: {result.files_installed} fontes instaladas")
        installer.update_font_cache()
        print("Cache de fontes atualizado")
        return 0
    else:
        print(f"\nErro: {result.message}")
        return 1


def list_fonts() -> int:
    """List installed fonts."""
    print("Fontes Instaladas")
    print("=" * 40)

    fonts = SystemChecker.list_installed_fonts()

    print("\n[Microsoft ClearType]")
    if fonts["microsoft"]:
        for font in fonts["microsoft"]:
            print(f"  {font}")
        print(f"  Total: {len(fonts['microsoft'])}")
    else:
        print("  (nenhuma)")

    print("\n[Developer Fonts]")
    if fonts["dev"]:
        for font in fonts["dev"]:
            print(f"  {font}")
        print(f"  Total: {len(fonts['dev'])}")
    else:
        print("  (nenhuma)")

    return 0


def main() -> int:
    """Main entry point."""
    args = sys.argv[1:]

    if not args:
        # Check dependencies before running TUI
        ok, missing = FontInstaller.check_dependencies()
        if not ok:
            print("Font Installer para Ubuntu")
            print("-" * 40)
            if not check_and_install_deps():
                return 1
            print()

        # Run TUI
        app = FontInstallerApp()
        app.run()
        return 0

    command = args[0].lower()

    if command in ("-h", "--help", "help"):
        print_help()
        return 0

    if command == "--install-deps":
        return install_deps_command()

    if command == "--cli":
        return run_cli_mode()

    if command == "list":
        return list_fonts()

    print(f"Comando desconhecido: {command}")
    print("Use 'font-installer --help' para ajuda")
    return 1
