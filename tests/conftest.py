import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure src/ is in sys.path for module resolution
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment variables from .env if present
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)
