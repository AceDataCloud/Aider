#!/usr/bin/env python3
"""Build an Ace-owned wheel/sdist without publishing to a package registry."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:a[0-9]+|b[0-9]+|rc[0-9]+)?", args.version):
        parser.error("use an explicit PEP 440 candidate version")
    output = args.out.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("output directory must be empty")
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["SETUPTOOLS_SCM_PRETEND_VERSION_FOR_ACEDATACLOUD_AIDER"] = args.version
    subprocess.run(
        [
            os.sys.executable,
            "-m",
            "build",
            "--no-isolation",
            "--sdist",
            "--wheel",
            "--outdir",
            str(output),
        ],
        cwd=ROOT,
        env=env,
        check=True,
    )
    wheel = next(output.glob("acedatacloud_aider-*.whl"))
    sdist = next(output.glob("acedatacloud_aider-*.tar.gz"))
    required = {
        "aider/acedatacloud.py",
        "aider/coders/base_coder.py",
        "aider/resources/model-settings.yml",
    }
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        assert required <= set(names), "wheel omitted native provider/runtime resources"
        metadata = archive.read(next(n for n in names if n.endswith(".dist-info/METADATA")))
        assert b"Name: acedatacloud-aider\n" in metadata
        entrypoints = archive.read(next(n for n in names if n.endswith("entry_points.txt")))
        assert b"ace-aider = aider.main:main" in entrypoints
        assert b"\naider =" not in entrypoints, "do not overwrite the official executable"
    with tarfile.open(sdist) as archive:
        assert any(n.endswith("/aider/acedatacloud.py") for n in archive.getnames())
    checksums = "".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
        for path in sorted((wheel, sdist))
    )
    (output / "SHA256SUMS").write_text(checksums)
    manifest = {
        "distribution": "acedatacloud-aider",
        "version": args.version,
        "executable": "ace-aider",
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "official_aider_release": False,
        "publisher": "Ace Data Cloud",
        "registry_upload": False,
        "artifacts": [wheel.name, sdist.name, "SHA256SUMS"],
    }
    (output / "release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
