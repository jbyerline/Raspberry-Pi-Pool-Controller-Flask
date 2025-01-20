import os
import logging
from pymongo import MongoClient

# Initialize logger
logger = logging.getLogger(__name__)
# TODO: Set the log level dynamically based on an environment variable
logger.setLevel(logging.DEBUG)

# Configure logger with a handler and format
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Load environment variables
def load_env_files():
    """Load environment variables from .env and .env.local if they exist."""
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get script's directory

    def load_env_file(filename):
        env_path = os.path.join(base_dir, filename)
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = map(str.strip, line.split('=', 1))
                        os.environ[key] = value
            print(f"Loaded environment variables from {env_path}")
        else:
            print(f"{env_path} not found, skipping")

    load_env_file('.env')
    load_env_file('.env.local')

load_env_files()


# MongoDB Configuration
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = os.environ.get("MONGO_DB_NAME")
COLLECTION_NAME = os.environ.get("MONGO_COLLECTION")

# Initialize MongoDB Client
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]
