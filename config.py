import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    # das aktuelle Verzeichnis holen
    project_path: Path = Path(__file__).resolve().parent
    # den Pfad des Bildes abrufen
    img_path: Path = project_path.joinpath("static", "img")
    # den Pfad des Inputs abrufen
    input_path: Path = project_path.joinpath("input")
    # Laden der .env-Dateien in die aktuelle Umgebung
    load_dotenv(project_path.joinpath(".env"))
    # get the api key from the environment
    api_key: str = os.getenv("API_KEY")

    # API URL
    api_url: str = "http://www.omdbapi.com/"

