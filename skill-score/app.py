from time import sleep

import streamlit
from st_pages import show_pages, Page
from streamlit_extras.switch_page_button import switch_page
from pages.utils import PagePath, get_engine, is_auth

from pages.utils import get_manager

if __name__ == "__main__":

    show_pages([Page(path=p.value, name=p.name) for p in PagePath])

    # some sleep
    sleep(0.1)

    # SQLAlchemy engine
    engine = get_engine()

    # creating cookie manager
    cookie_manager = get_manager()

    # switch page if authorized
    if is_auth(engine, cookie_manager):
        switch_page(PagePath.home.name)
    else:
        switch_page(PagePath.main.name)
