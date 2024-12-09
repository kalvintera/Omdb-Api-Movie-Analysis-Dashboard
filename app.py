import streamlit as st
import extra_streamlit_components as stx
import pandas as pd
from config import Config
from design.styler import DesignHandler
from api.omdb import OmdbApiHandler
from tabs.overview import initial_setup, create_overview_graphs
from tabs.details import create_details

# Initialisierung von Klassen und Konfigurationen
config = Config()
api = OmdbApiHandler()
designer = DesignHandler()

# Anpassung der Streamlit-Seiteneinstellungen
st.set_page_config(
    page_title="Film Analyse Dashboard", page_icon=":clapper:", layout="wide"
)

# Hinzufügen der eigenen CSS-Regeln
designer.add_custom_css()


# Initialisierung von Session State Variablen
if "movie_data_raw_df" not in st.session_state:
    st.session_state["movie_data_raw_df"] = pd.DataFrame()
    st.session_state["input_movie_titles"] = ""
    st.session_state["cleaned"] = False
    st.session_state["active_tab"] = "Overview"

# Seitenlayout und Inhalte
banner_container = st.container()
with banner_container:
    col_banner1, col_banner2 = banner_container.columns([1, 10])
    col_banner1.image(designer.logo, width=100, clamp=True, caption=None)
    col_banner2.title("Film Analyse Dashboard")

# Sidebar
movie_titles = st.sidebar.text_area(
    "Filme eingeben", "Geben Sie die Filmtitel ein, getrennt durch Kommas"
)
st.sidebar.subheader("ODER")
movie_file_upload = st.sidebar.file_uploader("Laden Sie eine IMDB Liste hoch")

start_analysis = st.sidebar.button("Analyse Starten")

# Navigation
chosen_id = stx.tab_bar(
    data=[
        stx.TabBarItemData(id=1, title="Overview", description=""),
        stx.TabBarItemData(id=2, title="Detail", description=""),
    ],
    default=1,
)

print(f"chosen_id : {chosen_id}")


# Wenn der 'Analyse Starten'-Button gedrückt wird
if start_analysis:
    if not st.session_state["movie_data_raw_df"].empty:
        st.session_state["movie_data_raw_df"] = pd.DataFrame()

        with st.spinner("Data loading..."):
            initial_setup(movie_titles, api, movie_file_upload)

    else:
        with st.spinner("Data loading..."):
            initial_setup(movie_titles, api, movie_file_upload)

# Wenn der Tab "Overview" gedrückt wurde
if chosen_id == str(1):
    if not st.session_state["movie_data_raw_df"].empty:
        create_overview_graphs()

# Wenn der Tab "Detail" gedrückt wurde
else:
    create_details()
