import bcrypt
import streamlit as st

from time import sleep
from sqlalchemy import select
from sqlalchemy.orm import Session
from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page

from pages.utils import PagePath, get_manager, get_engine, is_auth
from db.general_tables import User, Subject, TeacherInfo
from pages.auth.components import (email_input,
                                   subject_input,
                                   password_input,
                                   avatar_input,
                                   personal_info_input)


def main():
    # page configuration
    st.set_page_config(
        page_title="Регистрация",
        page_icon="📝",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # hiding pages
    hide_pages([_.name for _ in PagePath])

    # some sleep
    sleep(0.1)

    # num of succeed inputs
    success_count = 0

    # SQLAlchemy engine
    engine = get_engine()

    # creating cookie manager
    cookie_manager = get_manager()

    # switch page if authorized
    if is_auth(engine, cookie_manager):
        switch_page(PagePath.home.name)

    # page components
    st.title("Регистрация в Skill Score 📚")
    st.markdown("### Для учителей 🧑‍🏫")

    first_name, last_name, birth_date, success_count = personal_info_input(cookie_manager, success_count)

    email, success_count = email_input(cookie_manager, engine, success_count)

    col1, col2 = st.columns([5, 2])

    with col1:
        subject, success_count = subject_input(engine, success_count)
        password, success_count = password_input(success_count)

    with col2:
        avatar, success_count = avatar_input(success_count)

        if st.button("Завершить регистрацию", disabled=success_count != 6):
            with Session(engine) as session:
                user = User(
                    privilege_id=2,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    birth_date=birth_date,
                    hashed_password=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
                    avatar=avatar,
                    status=None
                )
                session.add(user)
                session.commit()

                teacher_info = TeacherInfo(
                    user_id=engine.connect().scalars(select(User.id).where(User.email == email)).all()[0],
                    subject_id=engine.connect().scalars(select(Subject.id).where(Subject.name == subject)).all()[0]
                )
                session.add(teacher_info)
                session.commit()
            switch_page(PagePath.registration_end.name)
        if st.button("Вернуться на главную страницу"):
            switch_page(PagePath.main.name)


if __name__ == "__main__":
    main()
