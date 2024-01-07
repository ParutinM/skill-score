from time import sleep

import streamlit as st
from sqlalchemy import select
from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page

from db.general_tables import User
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

    # SQLAlchemy engine
    engine = get_engine()

    # creating cookie manager
    cookie_manager = get_manager()

    # some sleep
    sleep(0.1)

    # switch page if authorized
    if not is_auth(engine, cookie_manager):
        switch_page(PagePath.main.name)

    st.markdown('<h1 style="text-align: center;font-size: 32px;">Это домашняя страница!</h1>',
                unsafe_allow_html=True)

    col1, _, col2 = st.columns([1, 2, 1])

    privilege_id = engine.connect().scalars(
        select(User.privilege_id).where(User.email == cookie_manager.get("email"))).all()[0]

    if st.button("Загрузить задачу", disabled=privilege_id < 2):
        switch_page(PagePath.load_task.name)

    if st.button("Выйти"):
        cookie_manager.delete("hashed_password")


if __name__ == "__main__":
    main()
