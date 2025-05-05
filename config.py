import os
from dotenv import load_dotenv
import sys
import logging
from typing import Optional

# Configure basic logging for config loading issues
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def get_env_var(var_name: str, default: Optional[str] = None, required: bool = False, var_type: type = str) -> any:
    """Helper function to get, validate, and type-cast environment variables."""
    value = os.getenv(var_name, default)
    if required and value is None:
        logger.critical(f"❌ Missing required environment variable: {var_name}")
        sys.exit(f"Error: Environment variable {var_name} is required but not set.")
    if value is not None:
        try:
            return var_type(value)
        except ValueError:
            logger.critical(f"❌ Invalid type for environment variable: {var_name}. Expected {var_type.__name__}, got '{value}'")
            sys.exit(f"Error: Invalid type for environment variable {var_name}.")
    return value # Return None if not required and not set

ADMIN_ID: int = get_env_var('ADMIN_ID', required=True, var_type=int) # Get ADMIN_ID from env
TOKEN: str = get_env_var('TOKEN', required=True)
DATABASE: str = get_env_var('DATABASE', required=True)
# Add other necessary variables like DB pool size if using pooling in database.py