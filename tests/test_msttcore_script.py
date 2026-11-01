"""Run the actual wrapper with fake RPM tools and no network/system changes."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize("missing_font", [None, "calibri.ttf", "comic.ttf"])
def test_wrapper_resolves_rpm_and_validates_staging(tmp_path, missing_font):
    bundle = tmp_path / "bundle with spaces"
    bundle.mkdir()
    script = Path(__file__).parents[1] / "src/font_installer/utils/msttcore.sh"
    shutil.copy2(script, bundle / "msttcore.sh")
    (bundle / "msttcore-fonts-installer-2.6-1.noarch.rpm").write_bytes(b"test rpm")
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "rpm2cpio").write_text(
        '#!/bin/bash\ntest -s "$1" || exit 1\nprintf payload\n'
    )
    (tools / "cpio").write_text("""#!/bin/bash
cat >/dev/null
mkdir -p usr/lib/msttcore-fonts-installer usr/share/fonts/msttcore
touch usr/share/fonts/msttcore/{arial,calibri,comic}.ttf
cat > usr/lib/msttcore-fonts-installer/refresh-msttcore-fonts.sh <<'REFRESH'
#!/bin/bash
[ "$1" = -d ] || exit 1
printf arial > "$2/arial.ttf"
if [ "${OMIT_FONT:-}" != calibri.ttf ]; then printf calibri > "$2/calibri.ttf"; fi
if [ "${OMIT_FONT:-}" != comic.ttf ]; then printf comic > "$2/comic.ttf"; fi
REFRESH
""")
    (tools / "fc-cache").write_text('#!/bin/bash\ntest "$1" = -f && test -d "$2"\n')
    for tool in tools.iterdir():
        tool.chmod(0o755)
    dest = tmp_path / "fonts with spaces"
    # A prior font must not mask a missing staged download.
    dest.mkdir()
    (dest / "calibri.ttf").write_bytes(b"old")
    env = dict(
        os.environ, PATH=f"{tools}:{os.environ['PATH']}", OMIT_FONT=missing_font or ""
    )
    result = subprocess.run(
        ["bash", str(bundle / "msttcore.sh"), str(dest)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    if missing_font:
        assert result.returncode != 0
        assert missing_font in result.stderr
        assert not (dest / "arial.ttf").exists()
        assert (dest / "calibri.ttf").read_bytes() == b"old"
    else:
        assert result.returncode == 0, result.stderr
        assert "FONT_INSTALLER_FILES_INSTALLED=3" in result.stdout
        assert (dest / "arial.ttf").read_bytes() == b"arial"
        assert (dest / "calibri.ttf").read_bytes() == b"calibri"
