.PHONY: install demo demo-auto test clean help

PY ?= python3

help:
	@echo "ClawShop dev shortcuts:"
	@echo "  make install     create .venv and install package + dev deps"
	@echo "  make test        run the full pytest suite"
	@echo "  make demo        run the interactive end-to-end demo (stub LLM)"
	@echo "  make demo-auto   run the demo non-interactively (auto-approves)"
	@echo "  make clean       remove .venv, caches, build artifacts"

.venv:
	$(PY) -m venv .venv
	./.venv/bin/pip install --upgrade pip
	./.venv/bin/pip install -e ".[dev]"

install: .venv
	@echo "Installed. Activate with: source .venv/bin/activate"

test: .venv
	./.venv/bin/pytest -q

demo: .venv
	LLM_MODE=stub ./.venv/bin/python -m clawshop demo

demo-auto: .venv
	@printf "Y\n" | LLM_MODE=stub ./.venv/bin/python -m clawshop demo

clean:
	rm -rf .venv .pytest_cache build dist *.egg-info clawshop.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
