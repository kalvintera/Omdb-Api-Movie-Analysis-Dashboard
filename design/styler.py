import streamlit as st
from PIL import Image
from config import Config


class DesignHandler:
    """
    Diese Klasse ist ein Beispiel, wie man Logik abkapseln kann.
    In dieser Klasse werden alle mit dem Einbinden von eigenem CSS verbundenen
    Funktionen und Werte an einer Stelle gebündelt. Die App
    muss nur die Haupt-Funktion "add_custom_css" aufrufen ohne mehr
    über die Implementierung wissen zu müssen.

    Aktuell gibt es nur eine staticmethod - die Klasse könnte aber leicht
    um mehr Logik und weitere Funktionen erweitert werden.
    """

    def __init__(self):
        self.config = Config()
        self.logo_path = self.config.img_path.joinpath("logo.jpg")
        self.logo = Image.open(self.logo_path)

    @staticmethod
    def add_custom_css():
        """Haupt-Method der Klasse, welche alle notwendigen custom-CSS-Regeln in
        das HTML einbindet."""
        st.markdown(
            """
            <style>

   
            .stDeployButton {
            display:none;
            }
            footer {
            visibility: hidden;
            }
            #stDecoration {
            display:none;
            }
            
            .font {
              font-size: 18px;
              font-family: cursive;
              color: white;
              }
            </style>
           
            """,
            unsafe_allow_html=True,
        )
