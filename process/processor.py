import json
import time
from typing import List, Tuple
import pandas as pd

from pyphoton import Photon

from config import Config
from pathlib import Path


class DataProcessor:
    def __init__(self, features_list: List[str]):
        """
        Konstruktor für DataProcessor-Klasse.
        :param features_list: Liste der Features, die aus den Filmdaten extrahiert werden sollen.
        """
        self.config = Config
        self.cache_file_path = Config.project_path.joinpath("processor").joinpath("location.cache.json")

        self.geo_locator = Photon()

        self.features_list = features_list

        self._load_cached_locations()

    def _load_cached_locations(self):
        self.geocache = {}

        if self.cache_file_path.exists():
            with open(self.cache_file_path, "r") as file:
                try:
                    self.geocache = json.loads(file.read())

                except json.JSONDecodeError:
                    print("Could not read cache file")

    def _update_cached_locations(self):
        with open(self.cache_file_path, "w") as file:
            file.write(json.dumps(self.geocache))

    def invalidate_cached_locations(self):
        self.cache_file_path.unlink()

    def list_from_selected_features(
        self,
        movie_data_list: List[dict],
    ) -> List[dict]:
        """
        Filtert Filme basierend auf ausgewählten Features.

        :param movie_data_list: Liste von Filmdaten als Dictionaries.
        :return: Liste von gefilterten Filmdaten.
        """

        # Initialisieren der Liste, die die gefilterten Filme aufnimmt
        movies_with_selected_features_list = []

        # Überprüfen, ob die Feature-Liste vorhanden ist
        if self.features_list:
            # Durchgehen jedes Films in der Liste
            for movie_dict in movie_data_list:
                # Ein Beispiel für eine komplexere List/Dictionary comprehension.
                # Das key-value-Paar wird nur hinzugefügt,
                # wenn der key auch in der self.features_lit vorkommt
                filtered_movie_dict = {
                    key: value
                    for key, value in movie_dict.items()
                    if key in self.features_list
                }

                movies_with_selected_features_list.append(filtered_movie_dict)

            return movies_with_selected_features_list

        else:
            print("Features list is empty.")
            return []

    @staticmethod
    def explode_column(df: pd.DataFrame, column_name_list: List) -> pd.DataFrame:
        """
        Wandelt als text gespeicherte Listen in Python Listen in den angegebenen Spalten um.

        :param df: Ursprünglicher DataFrame.
        :param column_name_list: Liste von Spaltennamen, deren Werte in Listen umgewandelt werden sollen.
        :return: Modifizierter DataFrame mit explodierten Spalten.
        """
        column_validator = [
            column_name for column_name in column_name_list if column_name in df.columns
        ]

        if column_validator:
            for column_name in column_validator:
                df[column_name] = df[column_name].apply(
                    lambda x: x.split(", ") if isinstance(x, str) else x
                )

            return df

        else:
            return df

    @staticmethod
    def process_ratings_list(movie_list: List[dict]) -> List[dict]:
        """
        Verarbeitet die Bewertungen der Filme.
        Die Bewertungen sind in einer einzelnen Liste mit einem Dictionary je Bewertung
        im Filmdaten-Dictionary hinterlegt.
        Diese Funktion hebt alle Bewertungen als eigenes key-value-pair auf die oberste Ebene.

        :param movie_list: Liste von Filmdaten.
        :return: Liste von Filmdaten mit verarbeiteten Bewertungen.
        """
        for movie in movie_list:
            if "Ratings" in movie.keys() and isinstance(movie["Ratings"], list):
                movie.update(
                    {
                        str(key) + " Rating": value
                        for key, value in movie["Ratings"].items()
                    }
                )
                del movie["Ratings"]
        return movie_list

    def get_coordinates(self, country: str) -> Tuple[None | int, None | int]:
        """
        Für das Land werden die Koordinaten über die API ermittelt.
        Ein dictionary als Instanzvariable dient als eigener Cache, um
        wiederholte API-Aufrufe für dasselbe Land zu verhindern.
        :param country:
        :return: Ein Tuple mit den Lat und Lon Werten des Landes
        """
        # Nur wenn das Land nicht bereits im Cache ist, wird eine API Anfrage ausgesendet.
        if country not in self.geocache:
            try:
                location = self.geo_locator.query(country, limit=1, osm_tags=["place:country"])
                time.sleep(0.1)

                if location:
                    self.geocache[country] = (location.latitude, location.longitude)
                    self._update_cached_locations()

            except Exception as e:
                print(f"Fehler beim Abrufen der Koordinaten für {country}: {e}")

        return self.geocache.get(country, (None, None))
