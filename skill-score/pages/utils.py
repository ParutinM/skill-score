import smtplib
import ssl
from time import sleep

import yaml

from enum import Enum
from pathlib import Path
from omegaconf import DictConfig

import streamlit as st
import extra_streamlit_components as stx
from extra_streamlit_components.CookieManager import CookieManager
from sqlalchemy import create_engine, Engine, select

from db.general_tables import User


@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()


@st.cache_resource
def get_engine():
    with open('db/config.yaml') as f:
        cfg = DictConfig(yaml.safe_load(f))

    engine = create_engine(f"{cfg.driver}://{cfg.host}:{cfg.port}/{cfg.database.name}")
    return engine


def send_verification_code(email: str, code: int):
    with open(Path(__file__).parent / "auth/config.yaml") as f:
        cfg = DictConfig(yaml.safe_load(f))

    message = f"Subject: Skill Score authentication code \n\nAuthentication code: {code}"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(cfg.smtp_server, cfg.port, context=context) as server:
        server.login(cfg.sender_email, cfg.password)
        server.sendmail(cfg.sender_email, email, message)


def is_auth(engine: Engine, cookie_manager: CookieManager) -> bool:
    email = cookie_manager.get("email")
    if email is None:
        return False
    cookie_hashed_password = cookie_manager.get("hashed_password")
    if cookie_hashed_password is None:
        return False
    hashed_password = engine.connect().scalars(select(User.hashed_password).where(User.email == email)).all()
    hashed_password = hashed_password[0] if len(hashed_password) > 0 else ""
    if cookie_hashed_password != str(hashed_password):
        return False
    return True


class PagePath(Enum):
    main = "pages/intro/main.py"
    registration_teacher = "pages/auth/registration_teacher.py"
    registration_student = "pages/auth/registration_student.py"
    registration_end = "pages/auth/registration_end.py"
    login = "pages/auth/login.py"
    home = "pages/home/home.py"
    load_task = "pages/home/load_task.py"


