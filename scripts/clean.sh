#!/bin/bash
set -euxo pipefail

poetry run isort quickpython/ tests/
poetry run black quickpython/ tests/
