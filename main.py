"""Entry point for AMS2 AI Creator."""

from ams2_ai.logging_config import setup_logging
from ams2_ai.ui.app import main

if __name__ == "__main__":
    setup_logging()
    raise SystemExit(main())
