import os

from app.client.api_gateway import Client
from dotenv import load_dotenv

load_dotenv()
CLIENT = Client(os.environ["API_URL"])