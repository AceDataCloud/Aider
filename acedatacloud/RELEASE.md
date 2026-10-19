# Ace-owned candidate distribution

This fork publishes **Ace Data Cloud candidates**, not official Aider AI releases.
The upstream provider contribution remains a separate branch and pull request.

## Install the GitHub Release artifact

Use a fresh Python 3.12 environment. Do not install this wheel alongside the
official `aider-chat` package: both contain the Python module `aider`.

```bash
uv venv --python 3.12 .venv-ace-aider
uv pip install --python .venv-ace-aider/bin/python \
  https://github.com/AceDataCloud/Aider/releases/download/ace-v0.86.3a20261019/acedatacloud_aider-0.86.3a20261019-py3-none-any.whl
.venv-ace-aider/bin/ace-aider --version
.venv-ace-aider/bin/ace-aider --list-models acedatacloud/
```

The distribution name is `acedatacloud-aider`, and its executable is `ace-aider`.
It does not replace the official `aider` executable or upload to the official
`aider-chat` PyPI namespace. Download `SHA256SUMS` and `release-manifest.json` from
the same release to verify the artifact and source commit. Availability begins
only when the release is public; a command printed here is not release evidence.

For a model request, provide your own `ACEDATACLOUD_API_KEY` through your secret
manager and choose a permitted exact model, for example:

```bash
.venv-ace-aider/bin/ace-aider --model acedatacloud/gpt-4.1
```

Model requests use account balance. Installation, `--version` and model discovery
do not require a key or a paid model call. The native provider has only been
validated with a free local fixture until separately documented otherwise.

## Build and release boundaries

All inherited upstream workflow jobs run only in `Aider-AI/aider`. In this fork,
they cannot publish PyPI/Docker images, deploy an `aider.chat` site, or run the
upstream issue-management script. The Ace artifact workflow only builds and
uploads a GitHub Actions artifact; it has read-only repository permissions and
does not publish to a registry or deploy a site.

The owner builds a versioned wheel/sdist using `scripts/build_ace_release.py`,
verifies a clean installation and local E2E, then attaches those files to a
clearly labeled GitHub prerelease in `AceDataCloud/Aider`. No publisher token or
new account is needed for that GitHub release. Future registry publication must
use a separately verified Ace-owned namespace and a dedicated publisher identity.

The provider PR branch used by the official submission must not be deleted or
updated with these fork-only packaging/workflow changes.
