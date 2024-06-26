import bcrypt
import streamlit as st

from sqlalchemy import select, Connection
from sqlalchemy.orm import Session

from skill_score.utils import PagePath, WebPage
from db.general_tables import User, Subject, TeacherInfo
from pages.auth.components import (email_input,
                                   subject_input,
                                   password_input,
                                   avatar_input,
                                   personal_info_input)


class RegistrationTeacherPage(WebPage):
    title = "Регистрация"
    icon = "📝"

    def _content(self, conn: Connection):
        success_count = 0

        st.title("Регистрация в Skill Score 📚")
        st.markdown("### Для учителей 🧑‍🏫")

        first_name, last_name, birth_date, success_count = personal_info_input(success_count)

        email, success_count = email_input(conn, success_count)

        col1, col2 = st.columns([5, 2])

        with col1:
            subject, success_count = subject_input(conn, success_count)
            password, success_count = password_input(success_count)

        with col2:
            avatar, success_count = avatar_input(success_count)

            if st.button("Завершить регистрацию", disabled=success_count != 6):
                with Session(conn.engine) as session:
                    user = User(
                        privilege_id=2,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        birth_date=birth_date,
                        hashed_password=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
                        avatar=avatar,
                        status=None,
                    )
                    session.add(user)
                    session.commit()

                    teacher_info = TeacherInfo(
                        user_id=conn.scalars(select(User.id).where(User.email == email)).all()[0],
                        subject_id=conn.scalars(select(Subject.id).where(Subject.name == subject)).all()[0]
                    )
                    session.add(teacher_info)
                    session.commit()

                if len(conn.scalars(select(User.id).where(User.email == email)).all()) > 0:
                    st.switch_page(PagePath.registration_end.value)
            if st.button("Вернуться на главную страницу"):
                st.switch_page(PagePath.main.value)


if __name__ == "__main__":
    page = RegistrationTeacherPage()
    page.show()
