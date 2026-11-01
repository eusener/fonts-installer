#!/bin/bash
# Extract the bundled installer RPM and install fonts for the current user.
set -euo pipefail

scriptdir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
rpmfile="$scriptdir/msttcore-fonts-installer-2.6-1.noarch.rpm"
fontdir="${1:-$HOME/.local/share/fonts/microsoft-core}"
fontdir=$(realpath -m -- "$fontdir")

for tool in rpm2cpio cpio cabextract curl fc-cache; do
    command -v "$tool" >/dev/null || { printf 'Dependência ausente: %s\n' "$tool" >&2; exit 1; }
done
[ -s "$rpmfile" ] || { printf 'RPM não encontrado: %s\n' "$rpmfile" >&2; exit 1; }

workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT
stagedir="$workdir/fonts"
mkdir -p "$stagedir"

printf 'Extraindo instalador do RPM local\n'
cd "$workdir"
rpm2cpio "$rpmfile" | cpio -id --quiet --no-absolute-filenames --no-preserve-owner
refresh="$workdir/usr/lib/msttcore-fonts-installer/refresh-msttcore-fonts.sh"
[ -s "$refresh" ] || { printf 'Instalador ausente no RPM\n' >&2; exit 1; }

# Only patch the temporary copy. Keep upstream checksum verification enabled.
sed -i 's#http://downloads.sourceforge.net/#https://downloads.sourceforge.net/#g' "$refresh"
# The upstream -d path extracts into staging but skips X11 and /etc configuration.
bash "$refresh" -d "$stagedir" -I "$workdir/installed-list.txt"
for required_font in arial.ttf calibri.ttf; do
    if [ ! -s "$stagedir/$required_font" ]; then
        printf 'Fonte obrigatória ausente: %s\n' "$required_font" >&2
        exit 1
    fi
done

# RPM payload font entries are the manifest; their placeholder contents are not fonts.
shopt -s nullglob
expected_fonts=("$workdir"/usr/share/fonts/msttcore/*.ttf)
[ "${#expected_fonts[@]}" -gt 0 ] || { printf 'Manifesto de fontes ausente no RPM\n' >&2; exit 1; }
for expected in "${expected_fonts[@]}"; do
    name="${expected##*/}"
    [ -s "$stagedir/$name" ] || { printf 'Fonte esperada ausente: %s\n' "$name" >&2; exit 1; }
done

mkdir -p "$fontdir"
count=0
for font in "$stagedir"/*.ttf; do
    [ -s "$font" ] || continue
    cp -- "$font" "$fontdir/"
    count=$((count + 1))
    printf 'FONT_INSTALLER_FILES_INSTALLED=%s\n' "$count"
done
printf 'Atualizando cache das fontes em %s\n' "$fontdir"
fc-cache -f "$fontdir"
