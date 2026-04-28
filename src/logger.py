import logging
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

handlers = [logging.StreamHandler()]

try:
    os.makedirs(LOG_DIR, exist_ok=True)
    handlers.insert(0, logging.FileHandler(LOG_FILE))
except OSError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=handlers,
)

logger = logging.getLogger("music_recommender")
