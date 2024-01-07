from time import sleep

import bcrypt
import streamlit as st

from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page
from pages.utils import PagePath, get_engine, get_manager, is_auth
from sqlalchemy import select
from db.general_tables import User


def main():
    # page configuration
    st.set_page_config(
        page_title="Вход в аккаунт",
        page_icon="📝",
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
    if is_auth(engine, cookie_manager):
        switch_page(PagePath.home.name)

    st.markdown('<h1 style="text-align: center;font-size: 32px;">Вход</h1>',
                unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        email = st.text_input(label="Адрес электронной почты",
                              value=cookie_manager.get("email"),
                              placeholder="example@test.com",
                              max_chars=30)

        password = st.text_input(label="Пароль",
                                 placeholder="Введите пароль",
                                 type="password",
                                 max_chars=30)

        hashed_password = engine.connect().scalars(select(User.hashed_password).where(User.email == email)).all()
        hashed_password = hashed_password[0] if len(hashed_password) > 0 else ""

        if st.button("Войти"):
            if bcrypt.checkpw(password.encode(), hashed_password.encode()):
                cookie_manager.set("email", email, key="email")
                cookie_manager.set("hashed_password", str(hashed_password), key="hashed_password")

                sleep(0.1)

                switch_page(PagePath.home.name)

            else:
                st.error("Неверная почта и/или пароль", icon="❌")

    with col2:
        if st.button("Войти в аккаунт"):
            switch_page(PagePath.main.name)


if __name__ == "__main__":
    main()
