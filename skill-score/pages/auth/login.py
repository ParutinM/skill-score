from time import sleep

import bcrypt
import json
import streamlit as st

from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from skill_score.utils import PagePath, get_cookie_manager, WebPage
from sqlalchemy import select, Connection, orm
from db.general_tables import User, Session


class LoginPage(WebPage):
    title = "Вход в аккаунт"
    icon = "📝"

    def _content(self, conn: Connection):
        st.markdown('<h1 style="text-align: center;font-size: 32px;">Вход</h1>',
                    unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])


        with col1:
            email = st.text_input(label="Адрес электронной почты",
                                  value=st.session_state.get("email"),
                                  placeholder="example@test.com",
                                  max_chars=30)

            password = st.text_input(label="Пароль",
                                     placeholder="Введите пароль",
                                     type="password",
                                     max_chars=30)

            hashed_password = conn.scalars(select(User.hashed_password).where(User.email == email)).all()
            hashed_password = hashed_password[0] if len(hashed_password) > 0 else bcrypt.gensalt().decode()

            if st.button("Войти"):
                if bcrypt.checkpw(password.encode(), hashed_password.encode()):
                    user_id = conn.scalars(select(User.id).where(User.email == email)).all()[0]
                    token = get_script_run_ctx().session_id
                    cookie_manager = get_cookie_manager()
                    cookie_manager.set("token", token, "token")
                    st.session_state.clear()
                    st.session_state["user_id"] = user_id
                    st.session_state["token"] = token
                    with orm.session.Session(conn.engine) as session:
                        if len(conn.scalars(select(Session.token).where(Session.user_id == user_id)).all()) == 0:
                            sess = Session(
                                user_id=user_id,
                                token=token,
                                state=json.dumps(st.session_state.to_dict())
                            )
                            session.add(sess)
                        else:
                            session.query(Session).filter(Session.user_id == user_id).update(
                                {"token": token, "state": json.dumps(st.session_state.to_dict())}
                            )
                        session.commit()
                    sleep(1)
                else:
                    st.error("Неверная почта и/или пароль", icon="❌")

            if st.session_state.get("token") == get_script_run_ctx().session_id:
                st.switch_page(PagePath.home.value)

        with col2:
            if st.button("Выйти в главное меню"):
                st.switch_page(PagePath.main.value)


if __name__ == "__main__":
    page = LoginPage()
    page.show()
