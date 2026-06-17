import sys
from pathlib import Path
import os

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(ROOT_DIR),
)

# Pour éviter qu'à l'import app.database pytest retry 20 fois la connexion Postgresql :
os.environ["DATABASE_URL"] = "postgresql+psycopg://test:test@localhost:5432/test"
