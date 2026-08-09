#!/bin/bash
set -eo pipefail

CYAN='\033[1;36m'
NC='\033[0m'


cyan_error() {
    >&2 echo -e "${CYAN}${1}${NC}"
}


cleanup() {
    set +x; cyan_error "Cleaning pycaches..."
    set -x; find hiscores_tracker lambda tests \
        \( -name '__pycache__' -o -name '*.pyc' \) -exec rm -rf {} +
}
trap 'cleanup' ERR


cyan_error "Checking types..."
(set -x; mypy hiscores_tracker lambda)

cyan_error "Running unit tests..."
(set -x; pytest tests lambda \
    --doctest-modules \
    --ignore-glob=lambda/*/handler.py \
    --cov=hiscores_tracker \
    --cov=lambda \
    --cov-report=html:.coverage_html
)

cyan_error "Enforcing formatters..."
(set -x; black hiscores_tracker lambda tests)
(set -x; isort hiscores_tracker lambda tests \
    --profile=black)

cyan_error "Checking linters..."
(set -x; flake8 hiscores_tracker lambda tests \
    --max-line-length=88 \
    --ignore=E203,W503)

cleanup
