import bcrypt
import streamlit as st

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.general_tables import User, Subject
from pages.auth.components import (email_input,
                                   subject_input,
                                   password_input,
                                   avatar_input,
                                   personal_info_input)
from skill_score.page import Page


class RegisterPage(Page):

    name = "register"

    def _not_authed_content(self):
        success_count = 0

        st.title("Регистрация в Skill Score 📚")
        st.markdown("### Для учителей 🧑‍🏫")

        first_name, last_name, birth_date, success_count = personal_info_input(success_count)

        email, success_count = email_input(self.conn, success_count)

        col1, col2 = st.columns([5, 2])

        with col1:
            subject, success_count = subject_input(self.conn, success_count)
            password, success_count = password_input(success_count)

        with col2:
            avatar, success_count = avatar_input(success_count)

            if st.button("Завершить регистрацию", disabled=success_count != 6, use_container_width=True):
                with Session(self.conn.engine) as session:
                    user = User(
                        privilege_id=2,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        birth_date=birth_date,
                        hashed_password=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
                        avatar=avatar,
                        status=None,
                        subject_id=self.conn.scalars(select(Subject.id).where(Subject.name == subject)).all()[0]
                    )
                    session.add(user)
                    session.commit()

                if len(self.conn.scalars(select(User.id).where(User.email == email)).all()) > 0:
                    self._switch_page("main")
            if st.button("Вернуться на главную страницу", use_container_width=True):
                self._switch_page("main")

    def _not_authed_sidebar_content(self):
        st.markdown("Hello")


if __name__ == "__main__":
    page = RegisterPage.from_toml()
    page.show()
