import streamlit as st
from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page
from pages.utils import PagePath


def main():
    hide_pages([_.name for _ in PagePath])

    st.markdown('<h1 style="text-align: center;font-size: 32px;">Поздравляем!</h1>',
                unsafe_allow_html=True)

    st.markdown('<h1 style="text-align: center;font-size: 24px;">Аккаунт успешно создан!</h1>',
                unsafe_allow_html=True)

    col1, _, col2 = st.columns([1, 2, 1])

    with col1:
        if st.button("Вернуться на главную страницу"):
            switch_page(PagePath.main.name)

    with col2:
        if st.button("Войти в аккаунт"):
            switch_page(PagePath.login.name)


if __name__ == "__main__":
    main()
