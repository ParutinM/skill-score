import smtplib
import ssl

from extra_streamlit_components.CookieManager import CookieManager
from sqlalchemy import create_engine

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx


class NoSessionError(Exception):
    pass


def get_session_id() -> str:
    ctx = get_script_run_ctx()
    if ctx is None:
        raise NoSessionError("Failed to get the thread context")
    return ctx.session_id


def get_ajs_anonymous_id() -> str:
    CookieManager(key="cookie_manager")
    try:
        cookie_manager = st.session_state.get("cookie_manager")
        ajs_anonymous_id = cookie_manager.get("ajs_anonymous_id")
        return ajs_anonymous_id
    except:
        st.rerun()


def get_sql_connection():
    cfg = st.secrets.connections.postgresql
    engine = create_engine(f"{cfg.dialect}://{cfg.username}:{cfg.password}@{cfg.host}:{cfg.port}/{cfg.database}")
    return engine.connect()


def send_verification_code(email: str, code: int):

    cfg = st.secrets.connections.smtp

    message = f"Subject: Skill Score authentication code \n\nAuthentication code: {code}"

    context = ssl.SSLContext()
    with smtplib.SMTP_SSL(cfg.host, cfg.port, context=context) as server:
        server.login(cfg.email, cfg.password)
        server.sendmail(cfg.email, email, message)
