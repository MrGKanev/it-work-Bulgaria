import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import git

# Simple configuration constants
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"
# CSV settings with expanded columns for detailed categories
CSV_COLUMNS = [
    "Date", "Site", "Total_Jobs", "Ruse_Jobs", "Remote_Jobs",
    "Categories_Count", "Categories_Detail", "Notes"
]
GIT_REPO_PATH = PROJECT_ROOT
GIT_COMMIT_MESSAGE_TEMPLATE = "Daily job count update for {date}"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)


def load_sites_config() -> Dict:
    """Load sites configuration from JSON file"""
    config_path = CONFIG_DIR / "sites.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Sites config file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in sites config: {e}")
        return {}


def get_csv_path(date: datetime) -> Path:
    """Get CSV file path for given date"""
    year = date.year
    month = date.strftime("%B")  # Full month name in English

    year_dir = DATA_DIR / str(year)
    year_dir.mkdir(exist_ok=True)

    return year_dir / f"{month}-{year}.csv"


def save_job_data(data_rows: List[Dict], date: datetime) -> Path:
    """Save job data to CSV file"""
    csv_path = get_csv_path(date)

    existing_data = []

    # Load existing data if file exists
    if csv_path.exists():
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                existing_data = list(reader)
        except Exception as e:
            logging.warning(f"Could not read existing CSV file: {e}")
            existing_data = []

    # Combine existing and new data
    all_data = existing_data + data_rows

    # Remove duplicates based on Date and Site (keep last occurrence)
    seen = {}
    unique_data = []

    for row in all_data:
        key = (row.get('Date'), row.get('Site'))
        seen[key] = row  # This will overwrite duplicates with latest

    unique_data = list(seen.values())

    # Sort by Date and Site
    unique_data.sort(key=lambda x: (x.get('Date', ''), x.get('Site', '')))

    # Write to CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        if unique_data:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(unique_data)
        else:
            # Write empty file with headers
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()

    logging.info(f"Data saved to {csv_path}")
    return csv_path


def commit_and_push_changes(file_path: Path, date: datetime) -> bool:
    """Commit and push changes to Git repository"""
    try:
        repo = git.Repo(GIT_REPO_PATH)

        # Check if file is tracked or new
        if file_path.relative_to(GIT_REPO_PATH).as_posix() not in repo.git.ls_files():
            # Add new file
            repo.git.add(str(file_path))
            logging.info(f"Added new file to git: {file_path}")
        else:
            # Add changed file
            repo.git.add(str(file_path))
            logging.info(f"Added changes to git: {file_path}")

        # Create commit message
        commit_message = GIT_COMMIT_MESSAGE_TEMPLATE.format(date=date.strftime("%Y-%m-%d"))

        # Check if there are changes to commit
        if repo.is_dirty():
            # Commit changes
            repo.git.commit('-m', commit_message)
            logging.info(f"Committed changes: {commit_message}")

            # Push to remote
            origin = repo.remote('origin')
            origin.push()
            logging.info("Pushed changes to remote repository")

            return True
        else:
            logging.info("No changes to commit")
            return True

    except git.InvalidGitRepositoryError:
        logging.error("Current directory is not a Git repository")
        return False
    except git.GitCommandError as e:
        logging.error(f"Git command failed: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during git operations: {e}")
        return False


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('job_tracker.log')
        ]
    )


def format_job_data_row(site: str, results: Dict, date: datetime, notes: str = "Daily scraping") -> Dict:
    """Format scraping results into CSV row format with detailed categories"""

    # Handle detailed category information
    categories_detail = ""
    categories_count = 0

    if 'raw_categories' in results and results['raw_categories']:
        categories = results['raw_categories']
        categories_count = len(categories)
        # Format as "cat1:123, cat2:456, cat3:789"
        categories_detail = ", ".join([f"{k}:{v}" for k, v in categories.items()])
    elif 'categories_detail' in results:
        categories_detail = results['categories_detail']

    return {
        'Date': date.strftime("%Y-%m-%d"),
        'Site': site,
        'Total_Jobs': results.get('total'),
        'Ruse_Jobs': results.get('ruse'),
        'Remote_Jobs': results.get('remote'),
        'Categories_Count': categories_count,
        'Categories_Detail': categories_detail,
        'Notes': notes
    }