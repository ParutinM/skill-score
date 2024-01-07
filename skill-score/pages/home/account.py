from time import sleep

import streamlit as st
from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page
from pages.utils import PagePath, get_manager, get_engine, is_auth


def main():
    st.set_page_config(
        page_title="Skill Score",
        page_icon="📚",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # hiding pages
    hide_pages([_.name for _ in PagePath])

    # some sleep
    sleep(0.1)

    # SQLAlchemy engine
    engine = get_engine()

    # creating cookie manager
    cookie_manager = get_manager()

    # switch page if authorized
    if not is_auth(engine, cookie_manager):
        switch_page(PagePath.main.name)

    st.markdown('<h1 style="text-align: center;font-size: 32px;">Профиль в Skill Score</h1>',
                unsafe_allow_html=True)

    col1, _, col2 = st.columns([1, 2, 1])



if __name__ == "__main__":
    main()
