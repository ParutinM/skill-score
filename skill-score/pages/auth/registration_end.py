import streamlit as st
from sqlalchemy import Connection
from st_pages import hide_pages
from skill_score.utils import PagePath, WebPage


class RegistrationEndPage(WebPage):
    title = "Регистрация"
    icon = "📝"

    def _content(self, conn: Connection):
        hide_pages([_.name for _ in PagePath])

        st.markdown('<h1 style="text-align: center;font-size: 32px;">Поздравляем!</h1>',
                    unsafe_allow_html=True)

        st.markdown('<h1 style="text-align: center;font-size: 24px;">Аккаунт успешно создан!</h1>',
                    unsafe_allow_html=True)

        col1, _, col2 = st.columns([1, 2, 1])

        with col1:
            if st.button("Вернуться на главную страницу"):
                st.switch_page(PagePath.main.value)

        with col2:
            if st.button("Войти в аккаунт"):
                st.switch_page(PagePath.login.value)


if __name__ == "__main__":
    page = RegistrationEndPage()
    page.show()
