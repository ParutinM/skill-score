from time import sleep

import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page
from pages.utils import PagePath, get_manager, get_engine, is_auth
from st_pages import hide_pages


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
    if is_auth(engine, cookie_manager):
        switch_page(PagePath.home.name)

    st.markdown(f'<h1 style="text-align: center;font-size: 108px;">Skill Score 📚</h1>',
                unsafe_allow_html=True)

    st.markdown(f'<h1 style="text-align: center;font-size: 36px;">Зарегистрируйся уже сейчас!</h1>',
                unsafe_allow_html=True)

    col1, _, col2 = st.columns([5, 1, 5])
    with col1:
        with stylable_container(
                key='student_reg',
                css_styles="""
                    {

                        background-color: #56BDED;
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        padding: calc(1em - 1px);
                        font_size: 60px;
                    }
                    """):
            st.markdown("""\
                #  Я - ученик 🙋

                $~$
                """)

        with stylable_container(
                key='student_registration',
                css_styles="""
                    button {
                        background-color: #56BDED;
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        font-size: 64px;
                    }
                    """):
            if st.button("***Регистрация***", use_container_width=True):
                switch_page(PagePath.registration_student.name)

    with col2:
        with stylable_container(
                key='teacher_reg',
                css_styles="""
                    {

                        background-color: #7741EC;
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        padding: calc(1em - 1px);
                        font_size: 60px;
                    }
                    """):
            st.markdown("""\
                # Я - учитель 🧑‍🏫

                $~$
                """)

        with stylable_container(
                key='teacher_registration',
                css_styles="""
                    button {
                        background-color: #7741EC;
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        font-size: 64px;
                    }
                    """):
            if st.button("***Регистрация*** ", use_container_width=True):
                switch_page(PagePath.registration_teacher.name)

    st.markdown(f'<h6 style="text-align: center;font-size: 24px;">Или войдите в аккаунт!</h6>',
                unsafe_allow_html=True)

    _, col3, _ = st.columns([3, 5, 3])

    with col3:
        with stylable_container(
                key='auth',
                css_styles="""
                    {

                        background-color: #F2A844;
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        padding: calc(1em - 1px);
                        font_size: 60px;
                    }
                    """):
            st.markdown("""\
                # Вход 

                $~$
                """)

        with stylable_container(
                key='authentication',
                css_styles="""
                    button {
                        background-color: #F2A844;
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        font-size: 64px;
                    }
                    """):
            if st.button("***Войти*** ", use_container_width=True):
                switch_page(PagePath.login.name)

    with st.sidebar:
        st.markdown(f'<h1 style="text-align: center;font-size: 32px;">Skill Score 📚</h1>',
                    unsafe_allow_html=True)

    if st.button("Регистрация для учителей"):
        switch_page(PagePath.registration_teacher.name)

    if st.button("Регистрация для учеников"):
        switch_page(PagePath.registration_student.name)


if __name__ == "__main__":
    main()
