import streamlit as st
import pandas as pd
import numpy as np
from typing import List
import plotly.express as px
import plotly.graph_objects as go
from process.processor import DataProcessor
from api.omdb import OmdbApiHandler


processor = DataProcessor([])


# Da die Ausführung dieser Funktion lange dauert, wird
# caching mit @st.cache_data verwendet, damit Länder nicht mehrfach verarbeitet werden
@st.cache_data
def get_country_coordinates(country: str):
    """Wrapper Funktion um get_coordinates mit caching"""
    return processor.get_coordinates(country)


def create_geo_map_data(country_list: List[str]) -> pd.DataFrame:
    """
    Erstellt aus einer Liste an Ländern ein DataFrame mit den Ländern und zugehörigen
    Lat und Lon Werten
    :param country_list: List an Länder-Codes
    :return: DataFrame
    """
    result_list = []
    for country in country_list:
        lat, lon = get_country_coordinates(country)
        if lat is not None and lon is not None:
            result_list.append({"country": country, "latitude": lat, "longitude": lon})

    return pd.DataFrame(result_list)


def update_movie_data(movie_titles_input: str, uploaded_file) -> List:
    """
    Aktualisiert die Filmdaten basierend auf dem eingegebenen Titel oder der hochgeladenen Datei.

    :param movie_titles_input: String mit durch Kommas getrennten Filmtiteln.
    :param uploaded_file: Hochgeladene Datei mit Filmtiteln.
    :return: Liste der Filmtitel.
    """
    movie_list = []

    if uploaded_file:
        # Datei basierend auf dem Dateityp lesen
        if uploaded_file.name.endswith(".csv"):
            movie_df = pd.read_csv(uploaded_file)

        elif uploaded_file.name.endswith(".xlsx"):
            movie_df = pd.read_excel(uploaded_file)

        else:
            # Erstellt ein leeres DataFrame, falls die Datei kein bekanntes Format hat
            movie_df = pd.DataFrame()

        # Wenn das DataFrame nicht leer ist und es eine "title" Spalte enthält
        # wird es weiter verwendet
        if not movie_df.empty and "Title" in movie_df.columns:
            movie_list = movie_df["Title"].tolist()

    # Wenn kein File hochgeladen wurde und stattdessen ein Filmtitel eingegeben wurde
    if not movie_list and movie_titles_input:
        # Verarbeite die eingegebenen Filmtitel
        movie_list = [title.strip() for title in movie_titles_input.split(",") if title]

    return movie_list


def initial_setup(movie_titles: str, api: OmdbApiHandler, movie_file_upload) -> None:
    """
    Initialisiert die Datenverarbeitung für die Streamlit-App.

    :param movie_titles: Eingegebene Filmtitel.
    :param api: Instanz der OmdbApiHandler-Klasse.
    :param movie_file_upload: Hochgeladene Datei mit Filmtiteln.
    """
    if (
        movie_titles != "Geben Sie die Filmtitel ein, getrennt durch Kommas"
        or movie_file_upload is not None
    ):
        movie_list = update_movie_data(
            movie_titles_input=movie_titles, uploaded_file=movie_file_upload
        )

        # Hier wird die Liste manuell reduziert, um das Testen der Applikation
        # zu erleichtern und das Überschreiten der API-Limits zu verhindern
        if len(movie_list) > 40:
            movie_list = movie_list[0:40]

        if movie_list and movie_list[0] != "":
            movie_data_raw = api.get_movie_info_from_list(movie_title_list=movie_list)

            if movie_data_raw:
                st.session_state.movie_data_raw_df = pd.DataFrame(movie_data_raw)
                print(
                    f"st.session_state.movie_data_raw_df {st.session_state.movie_data_raw_df}"
                )
                st.session_state.input_movie_titles = movie_list
            else:
                st.markdown(
                    '<p class="font">Movie not found!</p>', unsafe_allow_html=True
                )

        else:
            st.session_state.movie_data_raw_df = pd.DataFrame()
            st.session_state.input_movie_titles = ""
            st.markdown(
                '<p class="font">Your movie list is empty</p>', unsafe_allow_html=True
            )

    else:
        st.markdown('<p class="font">User input is missing</p>', unsafe_allow_html=True)


def create_overview_graphs() -> None:
    """
    Erstellt die Übersichtsgrafiken im Overview-Tab.
    """

    if not st.session_state.movie_data_raw_df.empty:
        st.session_state["active_tab"] = "Overview"

        st.subheader("Data Overview")
        st.markdown("<br>", unsafe_allow_html=True)

        st.session_state.movie_data_raw_df = processor.explode_column(
            df=st.session_state.movie_data_raw_df,
            column_name_list=["Genre", "Country", "Actors", "Country"],
        )

        # Geschützte Spalten:
        protected_columns = ["Poster", "Title", "Genre", "imdbRating", "BoxOffice"]

        # Df Filter-Elemente:
        filter_col1, filter_col2 = st.columns([1, 1])
        selected_columns = filter_col1.multiselect(
            "**Angezeigte Spalten**:",
            [
                column
                for column in st.session_state.movie_data_raw_df.columns
                if column not in protected_columns
            ],
        )

        text_search = filter_col2.text_input(
            "Suchen Sie Filme nach Titel, Genre oder Schauspieler", value=""
        )

        movie_data_raw_df = st.session_state.movie_data_raw_df.copy()

        if selected_columns:
            movie_data_raw_df = movie_data_raw_df[protected_columns + selected_columns]
        else:
            movie_data_raw_df = st.session_state.movie_data_raw_df

        if text_search:
            title_search = st.session_state.movie_data_raw_df.Title.str.contains(
                text_search, case=False
            )
            genre_search = st.session_state.movie_data_raw_df.Genre.str.contains(
                text_search, case=False
            )

            actor_search = st.session_state.movie_data_raw_df.Actors.str.contains(
                text_search, case=False
            )

            movie_data_raw_df_filtered = st.session_state.movie_data_raw_df[
                title_search | genre_search | actor_search
            ]
            movie_data_raw_df = movie_data_raw_df_filtered[movie_data_raw_df.columns]

        column_order = list(movie_data_raw_df.columns)

        column_order.remove("Poster")
        column_order.remove("Ratings")
        column_order.insert(0, "Poster")

        st.data_editor(
            movie_data_raw_df,
            column_order=column_order,
            column_config={
                "Poster": st.column_config.ImageColumn(
                    "Preview Poster", help="Streamlit app preview screenshots"
                ),
                "imdbRating": st.column_config.NumberColumn(
                    "imdbRating", help="IMDB Rating of the movie", format="%f ⭐"
                ),
            },
            hide_index=True,
        )

        st.subheader("Genre Analyse")
        graph_column_1, graph_column_2 = st.columns(2)
        graph_column_3, graph_column_4 = st.columns(2)

        with graph_column_1:
            # Die Spalte "Genre" in eine lange Reihe auflösen
            genre_exploded = st.session_state.movie_data_raw_df.explode("Genre")
            genre_counts = genre_exploded["Genre"].value_counts().reset_index()
            genre_counts.columns = ["Genre", "Count"]

            fig = px.bar(
                genre_counts,
                x="Count",
                y="Genre",
                orientation="h",
                title="Anzahl der Genres",
            )

            # Aktualisierung der x-Achse, um nur ganze Zahlen als Ticks anzuzeigen
            fig.update_layout(
                height=600,
                xaxis=dict(
                    dtick=1,  # Setzt die Tick-Intervalle auf ganze Zahlen
                    tick0=0,  # Beginnt die Ticks bei 0
                    range=[
                        0,
                        genre_counts["Count"].max() + 2,
                    ],  # Setzt die Reichweite der x-Achse
                ),
                yaxis=dict(
                    tickfont=dict(size=12),  # Schriftgröße der Tick-Labels anpassen
                ),
            )

            fig.update_traces(marker_color="purple", opacity=0.6)
            st.plotly_chart(fig, use_container_width=True)

            # Median IMDb-Bewertung pro Genre
            # Data-Bereinigen mit clean_int_values:
            genre_exploded = processor.clean_int_values(movie_df=genre_exploded)

            genre_ratings = (
                genre_exploded.groupby("Genre")["imdbRating"].median().reset_index()
            )

            genre_ratings = genre_ratings.sort_values(by="imdbRating", ascending=False)

            fig = px.bar(
                genre_ratings,
                x="imdbRating",
                y="Genre",
                orientation="h",
                title="Median IMDb-Bewertung pro Genre",
            )

            fig.update_layout(height=600)
            fig.update_traces(marker_color="navy", opacity=0.9)
            graph_column_2.plotly_chart(fig, use_container_width=True)

            # Korrelation zwischen Box-Office und Imdb Rating

            fig = px.scatter(
                genre_exploded,
                x="BoxOffice",
                y="imdbRating",
                hover_data=["Title"],
                title="Box-Office-Einnahmen vs. IMDb Bewertungen",
                trendline="ols",
                width=500,
                height=400,
            )
            graph_column_3.plotly_chart(fig)

            # Example Histogramm
            # Anzahl der Datenpunkte bestimmen
            movie_data_raw_df = processor.clean_int_values(movie_data_raw_df)
            bin_width = 10000000  # bin Breite - 10M
            bins = int((movie_data_raw_df["BoxOffice"].max() - float(movie_data_raw_df["BoxOffice"].min())) / bin_width)

            print(f"n_bins {bins}")
            graph_column_4.write("Verteilung der BoxOffice Einnahmen:")
            fig_hist = px.histogram(
                movie_data_raw_df,
                x="BoxOffice",
                nbins=bins,
                width=500,
                height=400
            )
            graph_column_4.plotly_chart(fig_hist)

            """
            # ADVANCE RESULTS 
            # Ergebnisse der Trendlinienanalyse
            results = px.get_trendline_results(fig)
            
            # Konvertiere die Ergebnisse in einen DataFrame
            results_df = results.px_fit_results.iloc[0].summary()
            
            # die Ergebnisse in Streamlit werden angezeigt
            graph_column_3.write("Trendlinienanalyse Ergebnisse:")
            graph_column_3.write(results_df)
            """

        # ----------  COUNTRIES MAP --------------

        # a dedicated single loader
        with st.spinner("Bitte warten ..."):
            countries = st.session_state.movie_data_raw_df["Country"].apply(
                lambda x: x.split(",") if isinstance(x, str) else x
            )
            processed_countries = list(
                set(country.strip() for country in set(countries.explode()))
            )

            geo_map_df = create_geo_map_data(country_list=processed_countries)

            # Erstellung der Mapbox-Karte
            fig = px.scatter_mapbox(
                geo_map_df,
                lat="latitude",
                lon="longitude",
                hover_data={"latitude": False, "longitude": False},
                zoom=1,
                height=500,
                title="Länderverteilung der Filme",
                color_discrete_sequence=["fuchsia"],
            )

            fig.add_trace(
                go.Scattermapbox(
                    mode="markers",
                    marker=go.scattermapbox.Marker(
                        size=15, color="rgb(242, 177, 172)", opacity=0.7
                    ),
                    hoverinfo="none",
                )
            )

            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                "<strong>Länderverteilung der Filme</strong>",
                unsafe_allow_html=True,
            )

            st.plotly_chart(fig, use_container_width=True)
