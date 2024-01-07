from time import sleep

import streamlit as st
from sqlalchemy import select, Engine
from sqlalchemy.orm import Session
from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page

from db.general_tables import SectionTree, TeacherInfo, User
from pages.utils import PagePath, get_manager, get_engine, is_auth


def section_tree(engine: Engine, subject_id: int, parent_id: int | None = None):
    children_ids = engine.connect().scalars(select(SectionTree.section_id)
                                            .where(SectionTree.subject_id == subject_id)
                                            .where(SectionTree.parent_id == parent_id)).all()
    children_names = engine.connect().scalars(select(SectionTree.section_name)
                                              .where(SectionTree.subject_id == subject_id)
                                              .where(SectionTree.parent_id == parent_id)).all()

    for child_id, child_name in zip(children_ids, children_names):
        with st.expander(label=child_name):
            st.text(child_name)
            section_tree(engine, subject_id, child_id)



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

    subject_id = engine.connect().scalars(
        select(TeacherInfo.subject_id)
        .join(User, TeacherInfo.user_id == User.id)
        .where(User.email == cookie_manager.get("email"))).all()[0]

    section_tree(engine, subject_id)

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        section = st.selectbox(label="Раздел",
                               placeholder="Выберите раздел",
                               options=engine.connect().scalars(
                                    select(SectionTree.section_name)
                                    .where(SectionTree.subject_id == subject_id)
                                    .where(SectionTree.parent_id.is_(None))).all(),
                               index=None)

    with col2:
        def change_adding():
            st.session_state.adding = not bool(st.session_state.get("adding"))

        st.button(label="Добавить новый раздел",
                  disabled=bool(st.session_state.get("adding")),
                  on_click=change_adding)

        if st.session_state.get("adding"):
            with col3:
                new_section = st.text_input(label="Новый раздел",
                                            placeholder="Введите название")
            with col4:
                if st.button(label="Добавить", disabled=new_section == ""):
                    with Session(engine) as session:
                        sec = SectionTree(
                            section_name=new_section,
                            subject_id=subject_id,
                            parent_id=None
                        )
                        session.add(sec)
                        session.commit()
                        st.session_state.adding = False
                        cookie_manager.set("email", cookie_manager.get("email"))

if __name__ == "__main__":
    main()
