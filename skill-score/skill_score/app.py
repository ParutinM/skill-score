import toml
import streamlit as st

from typing import List, Dict

from sqlalchemy import Connection

from skill_score.constants import PAGES_TOML_PATH
from skill_score.page import Page, PageInfo
from st_pages import hide_pages, show_pages


class App:

    initial_page_name: str = "main"

    def __init__(self, page_infos: List[PageInfo]):
        self.page_infos = page_infos

    @classmethod
    def from_toml(cls):
        with open(PAGES_TOML_PATH, "r") as toml_file:
            pages = [PageInfo(**page_config) for page_config in toml.load(toml_file)["page"].values()]
        return cls(pages)

    def init_pages(self):
        show_pages([page_info.view for page_info in self.page_infos])

    def get_page(self, name: str) -> PageInfo:
        for page_info in self.page_infos:
            if page_info.name == name:
                return page_info
        raise ValueError(f"Page with name '{name}' doesn't exist")

    def run(self):
        self.init_pages()
        st.switch_page(self.get_page(self.initial_page_name).path)
