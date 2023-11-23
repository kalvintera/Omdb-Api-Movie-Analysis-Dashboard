import requests
import json
from pathlib import Path
from typing import Dict, List
from config import Config


class OmdbApiHandler:
    """
    Diese Klasse dient als API-Wrapper und beinhaltet die gesamte Logik,
    um mit der API interagieren zu können. Die App muss nur die
    Funktionen dieser Klasse aufrufen, ohne wissen zu müssen, wie
    die Authentifizierung funktioniert oder Endpoints aufgebaut sind.
    """

    def __init__(self):
        self.config = Config()

        self.cache_file_location = Config.project_path.joinpath("api").joinpath("MovieData.cache.json")
        self._load_movie_data_cache()

    def _load_movie_data_cache(self):
        self.movie_data_cache = {}

        if self.cache_file_location.exists():
            with open(self.cache_file_location, "r") as file:

                try:
                    self.movie_data_cache = json.loads(file.read())
                except json.JSONDecodeError:
                    print(f"Could not read cached movie data.")

    def _update_movie_data_cache_file(self):
        with open(self.cache_file_location, "w") as file:
            file.write(json.dumps(self.movie_data_cache))

    def _invalidate_cached_movie_data(self):
        self.cache_file_location.unlink()

    def get_movie_data(self, movie_title: str) -> Dict:
        """
        Diese Funktion ruft die API auf und holt die Filmdaten basierend auf
        dem angegebenen Filmtitel.
        :param movie_title: der Filmtitel.
        :return: Ein Dictionary mit den Informationen des angegebenen Films
        """
        movie_data = self.movie_data_cache.get(movie_title, None)

        if movie_data:
            return movie_data

        parameters = {"t": movie_title, "apikey": self.config.api_key}

        try:
            request = requests.get(self.config.api_url, params=parameters)
            response = request.json()

            if "Response" in response.keys():
                if response["Response"] == "True":
                    self.movie_data_cache[movie_title] = response
                    self._update_movie_data_cache_file()
                    return response
                else:
                    return {}

        except (
            requests.exceptions.RequestException,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
        ) as error:
            print(f"Something went wrong while calling the api {error}")
            return {}

    def get_movie_info_from_list(self, movie_title_list: List[str]) -> List[dict]:
        """
        Diese Funktion iteriert durch die gegebene Filmliste und holt für jeden Film
        einzeln die Filmdaten über die API.
        :param movie_title_list: Liste an Filmtiteln.
        :return: Eine Liste mit einem Dictionary an Filmdaten je Film
        """
        movie_info_list = []

        if movie_title_list:
            for movie in movie_title_list:
                print(f"Fetching data from OmdbAPI for movie {movie}")

                movie_dict = self.get_movie_data(movie_title=movie)

                if len(movie_dict) > 0:
                    movie_info_list.append(movie_dict)
        else:
            print("No movie titles provided")

        return movie_info_list
