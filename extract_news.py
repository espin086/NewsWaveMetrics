import config
import logging
import os
from dotenv import load_dotenv


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(THIS_DIR)

# Load the .env file
load_dotenv("../../.env")

# Get the API key from the environment variable
RAPID_API_KEY = os.environ.get("RAPID_API_KEY")

