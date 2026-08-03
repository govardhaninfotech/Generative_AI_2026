import os
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# ===============================
# Database Configuration
# ===============================

DB_PATH = "chat.db"

# ===============================
# AI Model Configuration
# ===============================

MODEL = "llama-3.3-70b-versatile"

# ===============================
# Admin API Key
# ===============================

ADMIN_KEY = os.getenv(
    "ADMIN_API_KEY",
    "admin-secret-change-in-production"
)

# ===============================
# Logging Configuration
# ===============================

LOG_FILE = "app.log"

LOG_MAX_SIZE = 5 * 1024 * 1024

LOG_BACKUP_COUNT = 3