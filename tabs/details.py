import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS


def _create_cloud(text: str, max_word: int) -> None:
    """
    Erstellt eine Wortwolke aus gegebenem Text.

    :param text: Der zu visualisierende Text.
    :param max_word: Maximale Anzahl von Wörtern in der Wortwolke.
    :return: None
    """
    stopwords = set(STOPWORDS)

    # Ergänzen von eigenen STOPWORDS
    stopwords.update(
        {
            "us",
            "one",
            "will",
            "said",
            "now",
            "well",
            "man",
            "may",
            "little",
            "say",
            "must",
            "way",
            "long",
            "yet",
            "mean",
            "put",
            "seem",
            "asked",
            "made",
            "half",
            "much",
            "certainly",
            "might",
            "came",
        }
    )

    w_cloud = WordCloud(
        background_color="black",
        max_words=max_word,
        colormap="tab20c",
        stopwords=stopwords,
    )  # ,random_state=random

    # word cloud erstellen
    w_cloud.generate(text)

    # show the figure
    plt.figure(figsize=(100, 100))

    fig, ax = plt.subplots()
    ax.imshow(w_cloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)


def create_details() -> None:
    """
    Erstellt den Detail-Tab für die Streamlit-App.

    :return: None
    """
    st.session_state["active_tab"] = "Detail"

    if not st.session_state.movie_data_raw_df.empty:
        details_col1, details_col2 = st.columns(2)

        with details_col1:
            selected_title = st.selectbox(
                "Wählen Sie einen Film aus, um Details zu sehen:",
                st.session_state.movie_data_raw_df["Title"].unique(),
            )

            movie_details = st.session_state.movie_data_raw_df[
                st.session_state.movie_data_raw_df["Title"] == selected_title
            ].iloc[0]

            st.image(movie_details["Poster"])
            st.subheader(movie_details["Title"])
            st.write(f"**Year:** {movie_details['Year']}")
            st.write(f"**Rating:** {movie_details['Rated']}")
            st.write(f"**Released:** {movie_details['Released']}")
            st.write(f"**Runtime:** {movie_details['Runtime']}")
            st.write(f"**Genre:** {movie_details['Genre']}")
            st.write(f"**Director:** {movie_details['Director']}")
            st.write(f"**Plot:** {movie_details['Plot']}")
            st.write(f"**Awards:** {movie_details['Awards']}")
            st.write(f"**BoxOffice:** {movie_details['BoxOffice']}")

        with details_col2:
            if movie_details["Plot"] != "N/A" and movie_details["Plot"] is not None:
                st.subheader("Word Cloud Analyse")
                st.markdown(
                    '<p class="font">Die Wortwolke ist im Grunde eine Visualisierungstechnik zur '
                    "Darstellung der Häufigkeit von Wörtern in einem Text, wobei die Größe des "
                    "Wortes seine Häufigkeit darstellt.</p>",
                    unsafe_allow_html=True,
                )
                max_text_len = len(str(movie_details["Plot"]).split(" "))
                max_word = st.slider(
                    "maximale Anzahl an Wörter in der Wordcloud:",
                    5,
                    max_text_len,
                    int((max_text_len - 5) / 2),
                )

                _create_cloud(text=movie_details["Plot"], max_word=max_word)

            else:
                st.markdown(
                    '<p class="font">Plot not fount!</p>', unsafe_allow_html=True
                )
