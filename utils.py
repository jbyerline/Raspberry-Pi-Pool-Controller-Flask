import os
import logging

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
    def load_env_file(filename):
        if os.path.exists(filename):
            with open(filename) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = map(str.strip, line.split('=', 1))
                        os.environ[key] = value
            logger.info(f"Loaded environment variables from {filename}")
        else:
            logger.info(f"{filename} not found, skipping")

    load_env_file('.env')
    load_env_file('.env.local')

load_env_files()

