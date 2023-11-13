import streamlit as st
from PIL import Image
from config import Config


class DesignHandler:
    # Funktion, um benutzerdefiniertes CSS einzufügen
    def __init__(self):
        self.config = Config()
        self.logo_path = self.config.img_path.joinpath("logo.jpg")
        self.logo = Image.open(self.logo_path)

    @staticmethod
    def add_custom_css():
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
