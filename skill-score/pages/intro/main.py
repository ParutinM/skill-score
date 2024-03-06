import streamlit as st

from skill_score.page import Page
from skill_score.styles import styling


class MainPage(Page):

    name = "main"

    def _authed_content(self):
        self._switch_page("home")

    def _not_authed_content(self):
        st.markdown(*styling("Skill Score 📚", font_size=108))
        st.markdown(*styling("Платформа будущего"))


if __name__ == "__main__":
    page = MainPage.from_toml()
    page.show()
