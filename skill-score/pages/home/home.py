import datetime
import json
import streamlit as st
import streamlit_antd_components as sac
from sqlalchemy.orm import Session

from skill_score.page import Page, PageInfo
from skill_score.styles import styling

from sqlalchemy import select
from typing import List, Type

from db.general_tables import Privilege, Subject, TopicTree, TaskTag, TaskSource, AnswerType, Task, TaskSourceType
from pages.home.components.load_task import answer, task, solution, resource, topic, get_tree, task_view, load_task, ans_type
from pages.home.components.task import task_db_to_dict, task_widget, filter_task
from pages.home.components.configure import \
    (configure_sources,
     configure_tags,
     configure_topics,
     configure_view,
     configure_save)


class HomePage(Page):
    name = "home"

    menu_idx_to_name = {
        0: "Домашняя страница",
        1: "Задачи",
        2: "Банк задач",
        3: "Загрузка задач",
        4: "Конфигурация"
    }

    @property
    def load_state(self):
        if not self.authed_state.get("load", False):
            self.authed_state["load"] = {}
        return self.authed_state["load"]

    @property
    def conf_state(self):
        if not self.authed_state.get("conf", False):
            self.authed_state["conf"] = {}
        return self.authed_state["conf"]

    @property
    def bank_state(self):
        if not self.authed_state.get("bank", False):
            self.authed_state["bank"] = {}
        return self.authed_state["bank"]

    def _home_section(self):
        st.markdown(*styling("Это домашняя страница!"))

    def _tasks_bank_section(self):
        st.markdown(*styling("Банк задач"))
        with st.container(border=True):
            st.subheader("Фильтр")
            new_state = {
                "author_id": self.user.id,
                "subject": self.conn.scalars(select(Subject.name).where(Subject.id == self.user.subject_id)).one(),
                "subject_id": self.user.subject_id
            }
            col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
            with col1:
                new_state.update(topic(
                    label="Темы",
                    tree=get_tree(self.conn, self.user.subject_id),
                    multiple=True
                ))
            with col2:
                new_state.update(ans_type(
                    answer_types=self.conn.scalars(select(AnswerType.name)).all()
                ))
            with col3:
                st.markdown("###")
                new_state["my_flg"] = st.checkbox("Мои задачи")
            with col4:
                st.markdown("###")
                new_state["fav_flg"] = st.checkbox("Избранные")
            new_state.update(resource(
                conn=self.conn,
                show_extra=False
            ))
            st.markdown("###")
            _, col, _ = st.columns([2, 3, 2])
            with col:
                if st.button("Применить фильтр", use_container_width=True):
                    self.bank_state.update(new_state)
        st.divider()
        with Session(self.conn.engine) as session:
            tasks = [task_db_to_dict(self.conn, t) for t in session.query(Task).filter(
                Task.subject_id == self.bank_state.get("subject_id")).all()]
            for task_dict in tasks:
                if filter_task(task_dict, self.bank_state):
                    with st.container(border=True):
                        task_widget(task_dict)

    def _load_task_section(self):
        st.markdown(*styling("Загрузка задач"))
        new_state = {
            "author_id": self.user.id,
            "subject": self.conn.scalars(select(Subject.name).where(Subject.id == self.user.subject_id)).one(),
            "subject_id": self.user.subject_id
        }
        with st.container(border=True):
            st.subheader("1. Темы")
            new_state.update(topic(
                tree=get_tree(self.conn, self.user.subject_id),
                multiple=True))
        with st.container(border=True):
            st.subheader("2. Источник")
            new_state.update(resource(
                conn=self.conn,
                init_source_type=self.load_state.get("source_type"),
                init_source_extra=self.load_state.get("source_extra"),
                init_source=self.load_state.get("source"),
                init_tags=self.load_state.get("tags"),
            ))
        with st.container(border=True):
            st.subheader("3. Задача")
            new_state.update(task(
                init_symbols=self.load_state.get("symbols"),
                init_task=self.load_state.get("task"),
                init_task_name=self.load_state.get("task_name")
            ))
        with st.container(border=True):
            st.subheader("4. Решение")
            new_state.update(solution(
                init_solution=self.load_state.get("solution")
            ))
        with st.container(border=True):
            st.subheader("5. Ответ")
            new_state.update(answer(
                answer_types=self.conn.scalars(select(AnswerType.name)).all(),
                init_answer_type=self.load_state.get("answer_type"),
                init_answer=self.load_state.get("answer"),
                init_answer_extra=self.load_state.get("answer_extra")
            ))
        st.session_state["new_state"] = new_state
        with st.container(border=True):
            st.subheader("6. Превью")
            task_widget(new_state)
        self.load_state.update(new_state)
        st.divider()
        load_task(self.conn, new_state)

    def _configure_section(self):
        st.markdown(*styling("Конфигурация"))
        st.markdown(*styling("Эта страница про добавление/удаление тем, источников и т.д.", font_size=24))
        new_state = {
            "author_id": self.user.id,
            "subject": self.conn.scalars(select(Subject.name).where(Subject.id == self.user.subject_id)).one(),
            "subject_id": self.user.subject_id
        }
        with st.container(border=True):
            with st.container(height=60, border=False):
                tab_idx = sac.tabs(
                    items=[sac.TabsItem("Темы", icon="collection"),
                           sac.TabsItem("Источники", icon="dropbox"),
                           sac.TabsItem("Теги", icon="chat-left")],
                    align='center',
                    return_index=True,
                    color="cyan",
                    index=self.conf_state.get("tab_idx", 0),
                    use_container_width=True)

            if tab_idx == 0:
                new_state.update(configure_topics(
                    tree=get_tree(self.conn, self.user.subject_id),
                    tree_with_add=get_tree(self.conn, self.user.subject_id, with_add=True),
                    init_topics_to_add=self.conf_state.get("topics_to_add"),
                    init_topics_to_delete=self.conf_state.get("topics_to_delete"),
                ))
            elif tab_idx == 1:
                new_state.update(configure_sources(
                    conn=self.conn,
                    init_sources_to_add=self.conf_state.get("sources_to_add"),
                    init_sources_to_delete=self.conf_state.get("sources_to_delete"),
                    init_extras_to_add=self.conf_state.get("extras_to_add"),
                    init_extras_to_delete=self.conf_state.get("extras_to_delete")
                ))
            elif tab_idx == 2:
                new_state.update(configure_tags(
                    tags=self.conn.scalars(select(TaskTag.name)).all(),
                    init_tags_to_add=self.conf_state.get("tags_to_add"),
                    init_tags_to_delete=self.conf_state.get("tags_to_delete")
                ))
        self.conf_state.update(new_state)
        con = st.container()
        st.divider()
        self.conf_state.update(configure_save(self.conn, self.conf_state))
        with con:
            self.conf_state.update(configure_view(self.conf_state))

    def _authed_content(self):
        section = self.authed_state.get("menu_selected_section")
        if section == "Домашняя страница":
            self._home_section()
        elif section == "Банк задач":
            self._tasks_bank_section()
        elif section == "Загрузка задач":
            self._load_task_section()
        elif section == "Конфигурация":
            self._configure_section()

    def _sidebar_account_info(self):
        sac.divider(label='Аккаунт', icon='info-circle', align='center', color='gray')
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(*styling(self.user.avatar, font_size=64))
        with col2:
            st.markdown(*styling(" ".join([self.user.first_name, self.user.last_name]), tag="p", font_size=24))
            tags = []
            privilege = self.conn.scalars(select(Privilege.name).where(Privilege.id == self.user.privilege_id)).one()
            tags.append(sac.Tag(privilege, icon="person-fill", size="md", radius="md"))
            if self.user.privilege_id in [2, 3]:
                subject = self.conn.scalars(select(Subject.name)
                                            .where(Subject.id == self.user.subject_id)).one()
                tags.append(sac.Tag(subject, icon="book", size="md", radius="md"))
            sac.tags(tags, align="center")

    def _sidebar_menu(self):
        sac.divider(label='Меню', icon='layout-text-sidebar', align='center', color='gray')
        menu_idx = sac.menu([
            sac.MenuItem('Домашняя страница', icon='house-fill'),
            sac.MenuItem('Задачи', icon='box-fill', children=[
                sac.MenuItem('Банк задач', icon='database'),
                sac.MenuItem("Загрузка задач", icon='database-add', disabled=self.user.privilege_id < 3),
                sac.MenuItem("Конфигурация", icon='database-gear', disabled=self.user.privilege_id < 3),
            ]),
        ],
            index=self.authed_state.get("menu_selected_section_idx", 0),
            return_index=True,
            open_all=True,
            key="menu"
        )
        if menu_idx != self.authed_state.get("menu_selected_section_idx", 0):
            self.authed_state["menu_selected_section_idx"] = menu_idx
        self.authed_state["menu_selected_section"] = \
            self.menu_idx_to_name[self.authed_state.get("menu_selected_section_idx", 0)]

    def _sidebar_actual_page_options(self):
        if self.authed_state.get("menu_selected_section") == "Загрузка задач":
            sac.divider(label="Загрузка задач", icon='database-add', align='center', color='gray')
            if st.button("Сохранить введенные поля", use_container_width=True):
                self.load_state.update(st.session_state["new_state"])
            if st.button("Очистить введенные поля", use_container_width=True):
                self.load_state.clear()
                st.session_state["rerun"] = True

    def _authed_sidebar_content(self):
        st.markdown(*styling("Skill Score 📚"))
        self._sidebar_account_info()
        self._sidebar_menu()
        self._sidebar_actual_page_options()
        st.divider()
        _, col, _ = st.columns([1, 2, 1])
        if col.button("Выйти", use_container_width=True):
            self._quit()


if __name__ == "__main__":
    page = HomePage.from_toml()
    page.show()
