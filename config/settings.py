import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"
SCRAPERS_DIR = PROJECT_ROOT / "scrapers"

# CSV settings
CSV_COLUMNS = ["Date", "Site", "Total_Jobs", "Ruse_Jobs", "Remote_Jobs", "Notes"]

# Git settings
GIT_REPO_PATH = PROJECT_ROOT
GIT_COMMIT_MESSAGE_TEMPLATE = "Daily job count update for {date}"

# Request settings
REQUEST_TIMEOUT = 30
REQUEST_RETRIES = 3
REQUEST_DELAY = 1  # seconds between requests

# User Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)
SCRAPERS_DIR.mkdir(exist_ok=True)