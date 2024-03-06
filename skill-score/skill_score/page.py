import json
import time

import bcrypt
import toml
import st_pages
import streamlit as st
import streamlit_antd_components as sac

from typing import Literal, Type

from sqlalchemy.orm import Session

from skill_score.constants import PAGES_TOML_PATH, AUTHED, NOT_AUTHED
from skill_score.styles import styling, upload_button_style, center_zoom_picture, hide_links
from skill_score.utils import get_sql_connection, get_ajs_anonymous_id
from skill_score.test import test_email

from db.general_tables import Anonymous, User


class PageInfo:

    def __init__(self,
                 name: str,
                 path: str,
                 icon: str | None = None,
                 title: str | None = None,
                 layout: Literal["wide", "centered"] = "centered",
                 initial_sidebar_state: Literal["auto", "expanded", "collapsed"] = "auto"):
        self.name = name
        self.path = path
        self.icon = icon
        self.title = title
        self.layout = layout
        self.initial_sidebar_state = initial_sidebar_state

    @classmethod
    def from_toml(cls, name: str):
        with open(PAGES_TOML_PATH, "r") as toml_file:
            config = toml.load(toml_file)["page"][name]
        return cls(**config)

    @property
    def view(self):
        return st_pages.Page(self.path, self.name, self.icon)

    def to_config(self):
        return {"page_title": "Skill Score | " + self.title,
                "page_icon": self.icon,
                "layout": self.layout,
                "initial_sidebar_state": self.initial_sidebar_state}

    def __repr__(self):
        return f"PageInfo({self.__dict__})"


class Page:

    name: str

    def __init__(self, page_info: PageInfo):
        self.page_info = page_info
        st.set_page_config(**page_info.to_config())
        self.conn = get_sql_connection()
        self.anonymous = self._get_anonymous(get_ajs_anonymous_id())
        self.user = self._get_user()
        self.state = self._init_session_state()
        with open(PAGES_TOML_PATH, "r") as toml_file:
            self.all_pages = toml.load(toml_file)["page"]

    @classmethod
    def from_toml(cls):
        return cls(PageInfo.from_toml(cls.name))

    @staticmethod
    def _first_rerun():
        if st.session_state.get("rerun"):
            st.session_state["rerun"] = False
            st.rerun()

    @property
    def is_authed(self) -> bool:
        return self.anonymous.is_authed

    @property
    def authed_state(self) -> dict:
        if self.name:
            if self.name not in self.state[AUTHED]:
                self.state[AUTHED][self.name] = {}
            return self.state[AUTHED][self.name]
        raise AttributeError("Class should have non-empty attribute 'self.name'")

    @property
    def not_authed_state(self) -> dict:
        if self.name:
            if self.name not in self.state[NOT_AUTHED]:
                self.state[NOT_AUTHED][self.name] = {}
            return self.state[NOT_AUTHED][self.name]
        raise AttributeError("Class should have non-empty attribute 'self.name'")

    def _init_session_state(self):
        if self.name:
            state = {AUTHED: {}, NOT_AUTHED: {}}
            state[AUTHED][self.name] = {}
            state[NOT_AUTHED][self.name] = {}
            return state
        else:
            raise AttributeError("Class should have non-empty attribute 'self.name'")

    def _get_anonymous(self, ajs_anonymous_id: str) -> Type[Anonymous]:
        with Session(self.conn.engine) as session:
            anonymous = session.query(Anonymous).filter(Anonymous.ajs_id == ajs_anonymous_id).one_or_none()
            if anonymous is None:
                ss = st.session_state.to_dict()
                ss.pop("cookie_manager")
                new_anonymous = Anonymous(
                    ajs_id=ajs_anonymous_id,
                    state=json.dumps(ss),
                    is_authed=0
                )
                session.add(new_anonymous)
                session.commit()
                anonymous = self._get_anonymous(ajs_anonymous_id)
            return anonymous

    def _get_user(self) -> Type[User]:
        with Session(self.conn.engine) as session:
            user = session.query(User).filter(User.id == self.anonymous.user_id).one_or_none()
            return user

    def _load_state(self):
        self.state.update(json.loads(self.anonymous.state))

    def _save_state(self):
        with Session(self.conn.engine) as session:
            ss = self.state
            if "cookie_manager" in ss:
                ss.pop("cookie_manager")
            session.query(Anonymous).filter(Anonymous.ajs_id == self.anonymous.ajs_id) \
                .update({"state": json.dumps(ss)})
            session.commit()

    def _auth(self, password: str | None = None):
        if self.is_authed:
            return None
        email = self.not_authed_state.get("email")
        email_check, message = test_email(email, self.conn)
        if not email_check:
            sac.alert(label=message, icon="x-circle", color="red")
            return None
        with Session(self.conn.engine) as session:
            user: Type[User] = session.query(User).filter(User.email == email).one_or_none()
            session.commit()
            if user is None:
                sac.alert(label="Аккаунт с таким email не зарегестрирован", icon="x-circle", color="red")
                return None
            if bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
                session.query(Anonymous).filter(Anonymous.ajs_id == self.anonymous.ajs_id) \
                    .update({"user_id": user.id, "is_authed": 1})
                session.commit()
                self._switch_page("home")
            else:
                sac.alert(label="Неверный пароль", icon="x-circle", color="red")

    def _quit(self):
        if not self.is_authed:
            return None
        with Session(self.conn.engine) as session:
            session.query(Anonymous).filter(Anonymous.ajs_id == self.anonymous.ajs_id) \
                .update({"user_id": None, "is_authed": 0})
            session.commit()
            self._switch_page("main")

    def _switch_page(self, name: str):
        st.switch_page(self.all_pages[name]["path"])

    def _content(self):
        if self.is_authed:
            self._authed_content()
        else:
            self._not_authed_content()

    def _authed_content(self):
        pass

    def _not_authed_content(self):
        st.markdown(*styling("Skill Score 📚", font_size=108))
        st.markdown(*styling("Доступ запрещен", font_size=64))
        st.markdown(*styling("Для доступа к странице авторизируйтесь"))

    def _sidebar_content(self):
        if self.is_authed:
            self._authed_sidebar_content()
        else:
            self._not_authed_sidebar_content()

    def _authed_sidebar_content(self):
        pass

    def _not_authed_sidebar_content(self):
        st.markdown(*styling("Skill Score 📚"))
        sac.divider(label='Вход в аккаунт', icon='house', align='center', color='gray')
        mail = st.text_input(label="Почта", value=self.not_authed_state.get("email", ""))
        self.not_authed_state["email"] = mail
        password = st.text_input(label="Пароль", type="password")
        _, col, _ = st.columns([1, 2, 1])
        if col.button("Войти", use_container_width=True):
            self._auth(password)

    def show(self):
        self._first_rerun()
        self._load_state()
        upload_button_style()
        center_zoom_picture()
        hide_links()
        with st.sidebar:
            self._sidebar_content()
        self._content()
        self._save_state()

    def __repr__(self):
        return f"Page({self.__dict__})"
