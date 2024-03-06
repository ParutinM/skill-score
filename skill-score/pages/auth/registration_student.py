import bcrypt
import streamlit as st

from sqlalchemy import select, Connection
from sqlalchemy.orm import Session

from pages.auth.components import (email_input,
                                   region_school_input,
                                   personal_info_input,
                                   password_input,
                                   avatar_input,
                                   grade_input)
from skill_score.utils import PagePath, WebPage
from db.general_tables import User, School, StudentInfo


class RegistrationStudentPage(WebPage):
    title = "Регистрация"
    icon = "📝"

    def _content(self, conn: Connection):
        success_count = 0

        st.title("Регистрация в Skill Score 📚")
        st.markdown("### Для учеников 🙋")

        first_name, last_name, birth_date, success_count = personal_info_input(success_count)

        email, success_count = email_input(conn, success_count)

        region, school, success_count = region_school_input(conn, success_count)

        col1, col2 = st.columns([5, 2])
        with col1:
            grade, success_count = grade_input(success_count)
            password, success_count = password_input(success_count)

        with col2:
            avatar, success_count = avatar_input(success_count)
            if st.button("Завершить регистрацию", disabled=success_count != 8):
                with Session(conn) as session:
                    user = User(
                        privelege_id=1,
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

                    student_info = StudentInfo(
                        user_id=conn.scalars(select(User.id).where(User.email == email)).all()[0],
                        school_id=conn.scalars(select(School.id).where(School.name == school)).all()[0],
                        grade=grade,
                    )
                    session.add(student_info)
                    session.commit()
                st.switch_page(PagePath.registration_end.value)
            if st.button("Вернуться на главную страницу"):
                st.switch_page(PagePath.main.value)


if __name__ == "__main__":
    page = RegistrationStudentPage()
    page.show()
