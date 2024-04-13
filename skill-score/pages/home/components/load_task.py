import json
import re

import streamlit as st
import streamlit_antd_components as sac

from sqlalchemy import Connection, select
from sqlalchemy.orm import Session

from db.general_tables import TopicTree, TaskSourceType, TaskSource, TaskSourceExtra, TaskTag, Task, AnswerType

from pages.home.components.task import task_widget


def rerun():
    st.session_state["rerun"] = True


@st.experimental_fragment
def get_tree(conn: Connection,
             subject_id: int,
             parent_id: int | None = None,
             with_add: bool = False,
             deep: int = 0) -> list[sac.CasItem]:
    nodes = []

    children_ids = conn.scalars(select(TopicTree.id)
                                .where(TopicTree.subject_id == subject_id)
                                .where(TopicTree.parent_id == parent_id)
                                .order_by(TopicTree.name)).all()
    children_names = conn.scalars(select(TopicTree.name)
                                  .where(TopicTree.subject_id == subject_id)
                                  .where(TopicTree.parent_id == parent_id)
                                  .order_by(TopicTree.name)).all()

    for child_id, child_name in zip(children_ids, children_names):
        children = get_tree(conn, subject_id, child_id, with_add, deep + 1)
        nodes.append(sac.CasItem(label=f"{child_name}_{deep}",
                                 icon="clipboard",
                                 children=children if len(children) > 0 else None))

    if with_add:
        nodes.append(sac.CasItem(icon="clipboard-plus", label=f"..._{deep}"))

    return nodes


@st.experimental_fragment
def topic(tree: list[str | dict | sac.CasItem],
          label: str = "",
          multiple: bool = False):
    topics = sac.cascader(items=tree, label=label, multiple=multiple, placeholder="...", search=True,
                          format_func=lambda x: x.split("_")[0])
    topics = sorted(topics, key=lambda x: int(x.split("_")[1]))
    return {"topics": [x.split("_")[0] for x in topics]}


@st.experimental_fragment
def resource(conn: Connection,
             init_source_type: str | None = None,
             init_source: str | None = None,
             init_source_extra: dict | None = None,
             init_tags: list[str] | None = None,
             show_extra: bool = True,
             add_null: bool = False):
    if show_extra:
        col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    else:
        col1, col2, col4 = st.columns([1, 1, 1])
        col3 = None
    source_types = conn.scalars(select(TaskSourceType.name)).all()
    if add_null:
        source_types = ["..."] + list(source_types)
    if init_source_extra is None:
        init_source_extra = {}
    if init_tags is None:
        init_tags = []
    with col1:
        init_source_type_index = source_types.index(init_source_type) if init_source_type in source_types else None
        source_type = st.selectbox("Тип источника", source_types,
                                   index=init_source_type_index,
                                   placeholder="...")
    with col2:
        sources = conn.scalars(select(TaskSource.name)
                               .join(TaskSourceType, TaskSourceType.id == TaskSource.type_id)
                               .where(TaskSourceType.name == source_type)).all()
        if add_null:
            sources = ["..."] + list(sources)
        init_source_index = sources.index(init_source) if init_source in sources else None
        source = st.selectbox("Название источника", sources,
                              index=init_source_index,
                              placeholder="...",
                              disabled=source_type is None)
    source_extra = {}
    if show_extra:
        with col3:
            extras = conn.scalars(select(TaskSourceExtra.extra)
                                  .join(TaskSource, TaskSource.id == TaskSourceExtra.source_id)
                                  .where(TaskSource.name == source)).all()
            if source_type == "Олимпиада":
                col3_1, col3_2 = st.columns([1, 1])
                with col3_1:
                    init_stage = init_source_extra.get("stage")
                    stage_index = extras.index(init_stage) if init_stage in extras else None
                    source_extra["stage"] = st.selectbox("Этап", extras,
                                                         index=stage_index,
                                                         placeholder="...",
                                                         disabled=source is None)
                with col3_2:
                    source_extra["year"] = st.number_input("Год",
                                                           value=init_source_extra.get("year", 2000),
                                                           disabled=source is None)
            elif source_type == "Сборник задач":
                source_extra["num"] = st.text_input("Номер задачи из сборника",
                                                    value=init_source_extra.get("num", ""),
                                                    disabled=source is None)
            elif source_type == "Сайт":
                source_extra["extra"] = st.text_input("Дополнительная информация",
                                                      value=init_source_extra.get("url", ""),
                                                      disabled=source is None and not show_extra)
            elif source_type == "Экзамен":
                col3_1, col3_2 = st.columns([1, 1])
                with col3_1:
                    source_extra["extra"] = st.text_input("Дополнительная информация",
                                                          value=init_source_extra.get("extra", ""),
                                                          disabled=source is None and not show_extra)
                with col3_2:
                    source_extra["year"] = st.number_input("Год",
                                                           value=init_source_extra.get("year", 2000),
                                                           disabled=source is None)
    with col4:
        all_tags = conn.scalars(select(TaskTag.name)).all()
        init_tags = [_ for _ in init_tags if _ in all_tags]
        tags = st.multiselect("Tэги", all_tags, placeholder="...", default=init_tags)
    return {
        "source_type": source_type,
        "source": source,
        "source_extra": source_extra,
        "tags": tags
    }


@st.experimental_fragment
def task(init_task_name: str | None = "",
         init_task: str | None = "",
         init_symbols: dict[str, dict] | None = None):
    if init_task is None:
        init_task = ""
    if init_task_name is None:
        init_task_name = ""
    col1, col2 = st.columns([3, 1])
    with col1:
        task_name = st.text_input("Название", value=init_task_name)
        task_value = st.text_area("Условие", value=init_task)
        task_pic = st.file_uploader("Картинка к условию", type=['png', 'jpg'])
        task_pic_value = task_pic.getvalue() if task_pic else None
        st.session_state["task_pic"] = task_pic_value
        task_pic_name = ""
    with col2:
        try:
            if task_pic_value:
                con1 = st.container()
                con = st.container(border=True)
                task_pic_name = con1.text_input("Название картинки")
                task_pic_name = task_pic_name if task_pic_name else "Картинка к условию"
                con.image(task_pic_value,
                          caption=task_pic_name,
                          use_column_width=True)
            else:
                with st.container(border=True):
                    st.markdown("**Нет картинки**")
        finally:
            pass
    if init_symbols is None:
        init_symbols = {}
    symbols = sorted(list(set(re.findall(r'@(.*?)@', task_value))))
    symbols_dict = dict([(s, init_symbols.get(s, {})) for s in symbols])
    if len(symbols) > 0:
        st.divider()
        symbol = sac.tabs([sac.TabsItem(s, icon="pen") for s in symbols], align='center', use_container_width=True)
        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 5, 2, 2])
            with col2:
                step_options = [1, 0.1, 0.01]
                init_step = init_symbols.get(symbol, {}).get("step")
                step = st.radio("Шаг",
                                step_options,
                                key=f"step_{symbol}",
                                index=step_options.index(init_step) if init_step else 0)
            with col3:
                value = init_symbols.get(symbol, {}).get("values", (25, 75))
                values = st.slider(label='#',
                                   min_value=-100 * step,
                                   max_value=100 * step,
                                   value=(value[0] * step, value[1] * step),
                                   step=step,
                                   key=f"values_{symbol}")
                values = (int(values[0] / step), int(values[1] / step))
            with col4:
                power = st.number_input("Степень 10",
                                        step=3,
                                        value=init_symbols.get(symbol, {}).get("power", 0),
                                        key=f"power_{symbol}")
            with col1:
                left_bound = f"{round(values[0] * step, 3) if step != 1 else values[0]}" + \
                             ("\\cdot 10 ^ {" + f"{power}" + "}" if power else "")
                right_bound = f"{round(values[1] * step, 3) if step != 1 else values[1]}" + \
                              ("\\cdot 10 ^ {" + f"{power}" + "}" if power else "")
                st.markdown(f"##### ")
                st.markdown(f"##### ${symbol} \\in [{left_bound}, {right_bound}]$")
            with col5:
                st.markdown(f"##### ")
                if st.button(f"Сохранить значения для {symbol}"):
                    symbols_dict[symbol]["power"] = power
                    symbols_dict[symbol]["values"] = values
                    symbols_dict[symbol]["step"] = step
    return {
        "task_name": task_name,
        "task": task_value,
        "symbols": symbols_dict,
        "task_pic_name": task_pic_name,
    }


@st.experimental_fragment
def solution(init_solution: str | None = ""):
    if init_solution is None:
        init_solution = ""
    col1, col2 = st.columns([3, 1])
    with col1:
        solution_value = st.text_area("Решение", height=200, value=init_solution)
        solution_pic = st.file_uploader("Картинка к решению", type=['png', 'jpg'])
        solution_pic_value = solution_pic.getvalue() if solution_pic else None
        st.session_state["solution_pic"] = solution_pic_value
        solution_pic_name = ""
    with col2:
        try:
            if solution_pic_value:
                con1 = st.container()
                con = st.container()
                solution_pic_name = con1.text_input("Название картинки ")
                solution_pic_name = solution_pic_name if solution_pic_name else "Картинка к решению"
                con.image(solution_pic.getvalue(),
                          caption=solution_pic_name,
                          use_column_width=True)
            else:
                with st.container(border=True):
                    st.markdown("**Нет картинки** ")
        finally:
            pass
    return {
        "solution": solution_value,
        "solution_pic_name": solution_pic_name,
        "solution_pic": solution_pic_value,
    }


@st.experimental_fragment
def ans_type(answer_types: list[str],
             init_answer_type: str | None = None):
    init_answer_type_index = answer_types.index(init_answer_type) if init_answer_type in answer_types else None
    answer_type = st.selectbox("Тип ответа",
                               answer_types,
                               index=init_answer_type_index,
                               placeholder="...")
    return {"answer_type": answer_type}


@st.experimental_fragment
def answer(answer_types: list[str],
           init_answer_type: str | None = None,
           init_answer: str | float | None = "",
           init_answer_extra: dict | None = None):
    col1, col2 = st.columns([1, 3])
    with col1:
        answer_type = ans_type(answer_types, init_answer_type)["answer_type"]
    with col2:
        answer_extra = init_answer_extra if init_answer_extra else {}
        ans = init_answer
        if answer_type == "Формула":
            col2_1, col2_2, col2_3 = st.columns([5, 2, 1])
            with col2_1:
                ans = st.text_input("Ответ в виде формулы LaTeX")
            with col2_2:
                answer_extra["auto"] = st.checkbox("Автогенерация числового ответа по формуле", value=True)
            with col2_3:
                answer_extra["accuracy"] = st.number_input("Точность", value=3, disabled=not answer_extra["auto"])
        elif answer_type == "Текст":
            col2_1, col2_2 = st.columns([4, 1])
            with col2_1:
                ans = st.text_input("Ответ")
            with col2_2:
                st.markdown("##")
                answer_extra["full_match"] = st.checkbox("Точное совпадение")
        elif answer_type == "Число":
            col2_1, col2_3 = st.columns([6, 1])
            with col2_1:
                ans = st.text_input("Ответ в виде числа")
            with col2_3:
                answer_extra["accuracy"] = st.number_input("Точность", value=3)
        elif answer_type in ["Выбор", "Мультивыбор"]:
            col2_1, col2_2, col2_3, col2_4 = st.columns([3, 1, 3, 1])
            answer_extra["options"] = st.session_state.get("answer_choice_options", [])
            ans = st.session_state.get("answer_choice")
            with col2_1:
                option = st.text_input("Вариант ответа")
            with col2_2:
                st.markdown("##")
                if st.button("Добавить", disabled=len(option) == 0):
                    if option not in answer_extra["options"]:
                        answer_extra["options"].append(option)
            with col2_4:
                st.markdown("##")
                if st.button("Удалить", disabled=len(answer_extra["options"]) == 0):
                    if answer_type == "Выбор":
                        ans = [ans]
                    for option in ans:
                        if option in answer_extra["options"]:
                            answer_idx = answer_extra["options"].index(option)
                            answer_extra["options"].pop(answer_idx)
            with col2_3:
                if answer_type == "Выбор":
                    ans = st.radio("Варианты ответа:", answer_extra["options"])
                elif answer_type == "Мультивыбор":
                    ans = []
                    for option in answer_extra["options"]:
                        if st.checkbox(option):
                            ans.append(option)
            st.session_state["answer_choice_options"] = answer_extra["options"]
            st.session_state["answer_choice"] = ans
        elif answer_type == "Файл":
            col2_1, col2_2 = st.columns([2, 1])
            with col2_2:
                st.markdown("##")
                answer_extra["only_pdf"] = st.checkbox("Только файлы с разрешением .pdf")
        return {
            "answer_type": answer_type,
            "answer": ans,
            "answer_extra": answer_extra,
        }


@st.experimental_fragment
def task_view(state: dict):
    task_widget(state)


@st.experimental_fragment
def load_task(conn: Connection, state: dict):
    _, col, _ = st.columns([1, 2, 1])
    answer_type_id = conn.scalars(select(AnswerType.id)
                                  .where(AnswerType.name == state.get("answer_type"))).one_or_none()
    source_type_id = conn.scalars(select(TaskSourceType.id)
                                  .where(TaskSourceType.name == state.get("source_type"))).one_or_none()
    source_id = conn.scalars(select(TaskSource.id)
                             .where(TaskSource.name == state.get("source"),
                                    TaskSource.type_id == source_type_id)).one_or_none()
    task_ = Task(
        author_id=state.get("author_id"),
        subject_id=state.get("subject_id"),
        answer_type_id=answer_type_id,
        source_type_id=source_type_id,
        source_id=source_id,
        source_extra=json.dumps(state.get("source_extra")),
        topics=json.dumps(state.get("topics")),
        tags=json.dumps(state.get("tags")),
        name=state.get("task_name"),
        task=state.get("task"),
        symbols=json.dumps(state.get("symbols")),
        task_pic=st.session_state.get("task_pic"),
        task_pic_name=state.get("task_pic_name"),
        solution=state.get("solution"),
        solution_pic=st.session_state.get("solution_pic"),
        solution_pic_name=state.get("solution_pic_name"),
        answer=state.get("answer"),
        answer_extra=json.dumps(state.get("answer_extra"))
    )
    with col:
        if st.button("Загрузить задачу", use_container_width=True):
            try:
                with Session(conn.engine) as session:
                    session.add(task_)
                    session.commit()
                    st.success("Задача успешно загружена!")

            except:
                st.error("Не все поля введены или введены некорректно")
