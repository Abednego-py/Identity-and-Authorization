from dotenv import load_dotenv
import os

load_dotenv()

ALGORITHMS = os.environ.get("ALGORITHMS")
API_AUDIENCE = os.environ.get("API_AUDIENCE")
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
