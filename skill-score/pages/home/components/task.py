import json
from random import randint
from typing import List, Type

import streamlit as st
import streamlit_antd_components as sac
import sympy
from latex2sympy2 import latex2sympy
from sqlalchemy import Connection, select
from sqlalchemy.orm import Session

from db.general_tables import Task, AnswerType, TaskSource, TaskSourceType, Subject


def markd(text: str):
    with st.container(border=True):
        for s in text.split('\n\n'):
            s = s.strip()
            if len(s) > 0 and s[0] == s[-1] == '$':
                st.latex(s.replace('$', ''))
            else:
                st.markdown(s)


def text_and_image(text: str, image: bytes | None, image_name: str | None):
    if image:
        col01, col02 = st.columns([4, 1])
        with col01:
            markd(text)
        with col02:
            with st.container(border=True):
                try:
                    st.image(image,
                             use_column_width=True,
                             caption=image_name)
                finally:
                    pass
    else:
        markd(text)


def task_widget(state: dict):
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([4, 16, 1, 1])
        task_id = state.get('id', 'XXX')
        with col1:
            st.markdown(f"#### Задача №{task_id}")
            if state.get("task_name"):
                st.markdown(f'##### *"{state["task_name"]}"*')
        with col3:
            sac.rate(description='В избранное', value=0, align='end', color="yellow", count=1, size='lg',
                     key=f"rate1_{task_id}")
        with col4:
            sac.rate(description='Удалить', value=0, symbol=sac.BsIcon("trash"),
                     color="red", align='end', count=1, size='lg', key=f"rate2_{task_id}")
        with col2:
            sac.tags([sac.Tag(label=state.get("subject"), icon="book", color="blue")] +
                     [sac.Tag(label=t, icon="clipboard", color="blue") for t in state.get("topics")],
                     align="start", size=15, key=f"tags1_{task_id}" if task_id != 'XXX' else None)
            sac.tags([sac.Tag(label=state.get("source_type"), icon="collection", color="purple"),
                      sac.Tag(label=state.get("source"), icon="dropbox", color="purple")] +
                     [sac.Tag(label=v, icon="info-square", color="purple") for v in
                      state.get("source_extra", {}).values() if len(str(v)) > 0 and v is not None] +
                     [sac.Tag(label=state.get("answer_type"), icon="ui-checks", color="volcano")] +
                     [sac.Tag(label=tag, icon="chat-left", color="cyan") for tag in state.get("tags")],
                     align="start", size=15, key=f"tags2_{task_id}" if task_id != 'XXX' else None)
    mapping_task = {}
    task_transformed = state.get("task", "")
    if state.get("answer_extra", {}).get("auto"):
        if state.get("symbols", False):
            mapping_task = dict([(f"@{k}@",
                                  f"{round(randint(v.get('values', (25, 75))[0], v.get('values', (25, 75))[1]) * v.get('step', 1), 3)}" +
                                  ("\\cdot 10 ^ {" + f"{v.get('power', 0)}" + "}" if v.get('power', 0) else ""))
                                 for k, v in state["symbols"].items()])
        for k, v in mapping_task.items():
            task_transformed = task_transformed.replace(k, v)

    task_pic = state.get("task_pic") if state.get("task_pic") else st.session_state.get("task_pic")
    text_and_image(task_transformed, task_pic, state.get("task_pic_name"))

    with st.expander("Решение"):
        solution_pic = state.get("solution_pic") if state.get("solution_pic") else st.session_state.get("solution_pic")
        text_and_image(state.get("solution"), solution_pic, state.get("solution_pic_name"))

    with st.expander("Ответ"):
        if state.get("answer") and len(state.get("answer")) > 2 and state.get("answer_type") == "Формула":
            try:
                if state.get("answer_extra", {}).get("auto"):
                    subs = []
                    for k, v in mapping_task.items():
                        subs.append((sympy.Symbol(k[1:-1]), latex2sympy(v)))
                    ans = float(latex2sympy(state.get("answer")[1:-1]).subs(subs))
                    accuracy = state["answer_extra"].get("accuracy", 3)
                    eq = '=' if round(ans, accuracy) == ans else '\\approx'
                    st.markdown(state.get("answer")[:-1] + eq +
                                str(round(ans, accuracy) if ans != int(ans) else str(int(ans))) + '$')
                else:
                    st.markdown(state.get("answer"))
            except:
                st.error("Формула LaTeX введена некорректно")
        elif state.get("answer_type") in ["Выбор", "Мультивыбор"]:
            options = state.get("answer_extra", {}).get("options", [])
            ans = state.get("answer")
            if state.get("answer_type") == "Выбор":
                if ans in options:
                    ans_idx = options.index(ans)
                    st.radio("", options,
                             index=ans_idx,
                             disabled=True,
                             key=f"view_{ans_idx}",
                             label_visibility="collapsed")
            elif state.get("answer_type") == "Мультивыбор":
                for option in options:
                    st.checkbox(option, value=option in ans, disabled=True, key=f"view_{option}")
        elif state.get("answer_type") == "Число":
            st.markdown(f'${state.get("answer")}$')
        elif state.get("answer_type") == "Файл":
            st.markdown(f'Загрузка в виде файла')
        else:
            st.markdown(state.get("answer"))


def task_db_to_dict(conn: Connection, task: Task | Type[Task]) -> dict:
    state = task.__dict__
    state["task_name"] = state["name"]
    state["answer_type"] = conn.scalars(select(AnswerType.name)
                                        .where(AnswerType.id == state["answer_type_id"])).one()
    state["source_type"] = conn.scalars(select(TaskSourceType.name)
                                        .where(TaskSourceType.id == state["source_type_id"])).one()
    state["source"] = conn.scalars(select(TaskSource.name)
                                   .where(TaskSource.id == state["source_id"])).one()
    state["subject"] = conn.scalars(select(Subject.name)
                                    .where(Subject.id == state["subject_id"])).one()
    for param in ["source_extra", "topics", "tags", "answer_extra", "symbols"]:
        state[param] = json.loads(state[param])

    return state


def filter_task(task_dict: dict, filter_state: dict) -> bool:
    def in_filter_state(name: str) -> bool:
        return task_dict.get(name) == filter_state.get(name) if filter_state.get(name) else True

    res = all([all([topic in task_dict.get("topics", []) for topic in filter_state.get("topics")]),
               in_filter_state("answer_type"),
               in_filter_state("source_type"),
               in_filter_state("source"),
               all([tag in task_dict.get("tags", []) for tag in filter_state.get("tags")]),
               task_dict.get("author_id") == filter_state.get("author_id") if filter_state.get("my_flg") else True,
               ])
    return res
