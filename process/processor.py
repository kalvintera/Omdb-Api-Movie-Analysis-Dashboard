from typing import List
import geopy.exc
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


geocache = set()


class DataProcessor:
    def __init__(self, features_list: List):
        """
        Konstruktor für DataProcessor-Klasse.

        :param features_list: Liste der Features, die aus den Filmdaten extrahiert werden sollen.
        """
        self.features_list = features_list
        self.geolocator = Nominatim(user_agent="myGeocoder", timeout=10)
        self.geolocator = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)
        self.geocache = {}

    # List comprehension Beispiel
    def list_from_selected_features(
        self,
        movie_data_list: List,
    ) -> List:
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
                filtered_movie_dict = {
                    key: value
                    for key, value in movie_dict.items()
                    if key in self.features_list
                }

                movies_with_selected_features_list.append(filtered_movie_dict)
            return movies_with_selected_features_list
        else:
            print("Features list is empty.")

    @staticmethod
    def explode_column(df: pd.DataFrame, column_name_list: List):
        """
        Explodiert Spalten im DataFrame, die Listen von Werten enthalten.

        :param df: Ursprünglicher DataFrame.
        :param column_name_list: Liste von Spaltennamen zum Explodieren.
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
    def process_ratings_list(movie_list: List):
        """
        Verarbeitet die Bewertungen der Filme.

        :param movie_list: Liste von Filmdaten.
        :return: Liste von Filmdaten mit verarbeiteten Bewertungen.
        """
        for movie in movie_list:
            if "Ratings" in movie.keys() and type(movie_list) == list:
                movie.update(
                    {str(key) + " Rating": value for key, value in movie.items()}
                )
                del movie["Ratings"]
        return movie_list

    # PROCESSING FOR MAP

    def get_coordinates(self, country):
        if country not in self.geocache:
            try:
                location = self.geolocator(country)
                if location:
                    self.geocache[country] = (location.latitude, location.longitude)
            except Exception as e:
                print(f"Fehler beim Abrufen der Koordinaten für {country}: {e}")
        return self.geocache.get(country, (None, None))
