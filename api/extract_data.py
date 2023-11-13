import requests
from typing import Dict, List
from config import Config


class OmdbApiHandler:
    def __init__(self):
        self.config = Config()

    def get_movie_data(self, movie_title: str) -> Dict:
        """
        this function calls an api and gets information based on given movie title
        :param movie_title: a string / represents the title of the movie
        :return: a dictionary with meta information of the given movie title
        """
        parameters = {"t": movie_title, "apikey": self.config.api_key}
        try:
            request = requests.get(self.config.api_url, params=parameters)
            response = request.json()

            if "Response" in response.keys():
                if response["Response"] == "True":
                    return response
                else:
                    return {}
        except (
            requests.exceptions.RequestException,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
        ) as error:
            print(f"Something went wrong while calling the api {error}")

    def get_movie_info_from_list(self, movie_title_list) -> List:
        """
        this function iterates through a string list, extracts movie information from
        each movie title
        :param movie_title_list: a string list contains movie titles
        :return: a list of dictionaries with movie information
        """
        movie_info_list = []
        if movie_title_list:
            for movie in movie_title_list:
                movie_dict = self.get_movie_data(movie_title=movie)
                if len(movie_dict) > 0:
                    movie_info_list.append(movie_dict)
        else:
            print("movie title is empty")

        if movie_info_list:
            return movie_info_list
        else:
            print("movie info for given movie titles")
