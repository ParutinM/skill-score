import streamlit as st
import streamlit_antd_components as sac
from sqlalchemy import Connection, select
from sqlalchemy.orm import Session

from db.general_tables import TaskSourceType, TaskSource, TopicTree, TaskSourceExtra, TaskTag
from skill_score.styles import styling


def configure_topics(tree: list[sac.CasItem],
                     tree_with_add: list[sac.CasItem],
                     init_topics_to_delete: list[str] | None = None,
                     init_topics_to_add: list[str] | None = None):
    actions = [
        {
            "label": "Добавить подтему",
            "icon": "clipboard-plus"
        },
        {
            "label": "Удалить тему",
            "icon": "clipboard-x"
        }
    ]
    with st.container():
        with st.container(height=60, border=False):
            action_idx = sac.tabs(
                items=[sac.TabsItem(**param) for param in actions],
                align='center',
                return_index=True,
                use_container_width=True)
        topics_to_delete = init_topics_to_delete if init_topics_to_delete else []
        topics_to_add = init_topics_to_add if init_topics_to_add else []
        if actions[action_idx]["label"] == 'Удалить тему':
            with st.empty():
                topic = sac.cascader(items=tree,
                                     label="Выберите тему",
                                     multiple=False,
                                     placeholder="...",
                                     search=True,
                                     format_func=lambda x: x.split("_")[0])
            topic = [x.split("_")[0] for x in topic]
            if st.button(f'Удалить тему "{" / ".join(topic)}"',
                         use_container_width=True,
                         disabled=len(topic) == 0):
                if ' / '.join(topic) not in topics_to_delete:
                    topics_to_delete.append(' / '.join(topic))
        elif actions[action_idx]["label"] == 'Добавить подтему':
            with st.empty():
                topic = sac.cascader(items=tree_with_add,
                                     label="Выберите тему",
                                     multiple=False,
                                     placeholder="...",
                                     search=True,
                                     format_func=lambda x: x.split("_")[0])
            topic = [x.split("_")[0] for x in topic]
            col1_1, col1_2 = st.columns([3, 1])
            with col1_1:
                subtopic = " / ".join(topic[:-1] + [st.text_input("Новая подтема", disabled=len(topic) == 0)])
            with col1_2:
                st.markdown(*styling("", font_size=24))
                if st.button("Добавить", use_container_width=True, disabled=len(topic) == 0):
                    if subtopic not in topics_to_add:
                        topics_to_add.append(subtopic)
    return {
        "action_idx": action_idx,
        "topics_to_delete": topics_to_delete,
        "topics_to_add": topics_to_add
    }


def configure_sources(conn: Connection,
                      init_source_type_index: int = 0,
                      init_sources_to_delete: dict | None = None,
                      init_sources_to_add: dict | None = None,
                      init_extras_to_delete: dict | None = None,
                      init_extras_to_add: dict | None = None
                      ):
    source_types = conn.scalars(select(TaskSourceType.name)).all()
    with st.container(height=60, border=False):
        source_type_idx = sac.tabs(
            items=[sac.TabsItem(source_type, icon="bookmark") for source_type in source_types],
            align='center',
            return_index=True,
            index=init_source_type_index,
            color='lime',
            use_container_width=True)
    source_type = source_types[source_type_idx]
    type_id = conn.scalars(select(TaskSourceType.id).where(TaskSourceType.name == source_type)).one()
    sources = conn.scalars(select(TaskSource.name).where(TaskSource.type_id == type_id)).all()

    sources_to_delete = init_sources_to_delete if init_sources_to_delete else dict([(x, []) for x in source_types])
    sources_to_add = init_sources_to_add if init_sources_to_add else dict([(x, []) for x in source_types])
    extras_to_delete = init_extras_to_delete if init_extras_to_delete else dict([(x, []) for x in source_types])
    extras_to_add = init_extras_to_add if init_extras_to_add else dict([(x, []) for x in source_types])
    with st.container():
        if source_type == "Олимпиада":
            with st.container(height=60, border=False):
                action = sac.tabs(
                    items=[sac.TabsItem("Добавить олимпиаду", "clipboard-plus"),
                           sac.TabsItem("Добавить этап олимпиады", "clipboard-plus"),
                           sac.TabsItem("Удалить олимпиаду", "clipboard-x"),
                           sac.TabsItem("Удалить этап олимпиады", "clipboard-x")
                           ],
                    align='center',
                    use_container_width=True)

            if action == "Удалить олимпиаду":
                source = st.selectbox("Выберите олимпиаду", sources, index=None, placeholder="...")
                if st.button(f'Удалить олимпиаду "{source}"', use_container_width=True, disabled=source is None):
                    sources_to_delete[source_type].append(source)

            elif action == "Удалить этап олимпиады":
                source = st.selectbox("Выберите олимпиаду", sources, index=None, placeholder="...")
                source_id = conn.scalars(select(TaskSource.id).where(TaskSource.name == source,
                                                                     TaskSource.type_id == type_id)).one()
                extras = conn.scalars(select(TaskSourceExtra.extra)
                                      .where(TaskSourceExtra.source_id == source_id)).all()
                extra = st.selectbox("Выберите этап олимпиады", extras, index=None, placeholder="...")
                if st.button(f'Удалить этап "{extra}" олимпиады "{source}"',
                             use_container_width=True, disabled=source is None):
                    extras_to_delete[source_type].append((source, extra))

            elif action == "Добавить олимпиаду":
                source = st.text_input("Название олимпиады")
                if st.button("Добавить", use_container_width=True, disabled=source is None):
                    if source not in sources_to_add:
                        sources_to_add[source_type].append(source)

            elif action == "Добавить этап олимпиады":
                source = st.selectbox("Выберите олимпиаду", sources, index=None, placeholder="...")
                extra = st.text_input("Название этапа олимпиады", disabled=source is None)
                if st.button(f'Добавить этап "{extra}" олимпиады "{source}"',
                             use_container_width=True, disabled=source is None):
                    extras_to_add[source_type].append((source, extra))
        elif source_type == "Сборник задач":
            with st.container(height=60, border=False):
                action = sac.tabs(
                    items=[sac.TabsItem("Добавить сборник задач", "clipboard-plus"),
                           sac.TabsItem("Удалить сборник задач", "clipboard-x")
                           ],
                    align='center',
                    use_container_width=True)

            if action == "Удалить сборник задач":
                source = st.selectbox("Выберите сборник задач", sources, index=None, placeholder="...")
                if st.button(f'Удалить сборник задач "{source}"', use_container_width=True, disabled=source is None):
                    sources_to_delete[source_type].append(source)

            elif action == "Добавить сборник задач":
                source = st.text_input("Автор / название сборника задач")
                if st.button("Добавить", use_container_width=True, disabled=source is None):
                    if source not in sources_to_add:
                        sources_to_add[source_type].append(source)

        elif source_type == "Сайт":
            with st.container(height=60, border=False):
                action = sac.tabs(
                    items=[sac.TabsItem("Добавить сайт", "clipboard-plus"),
                           sac.TabsItem("Удалить сайт", "clipboard-x")
                           ],
                    align='center',
                    use_container_width=True)

            if action == "Удалить сайт":
                source = st.selectbox("Выберите сайт", sources, index=None, placeholder="...")
                if st.button(f'Удалить сайт "{source}"', use_container_width=True, disabled=source is None):
                    if source not in sources_to_delete:
                        sources_to_delete[source_type].append(source)

            elif action == "Добавить сайт":
                source = st.text_input("Название сайта")
                if st.button("Добавить", use_container_width=True, disabled=source is None):
                    if source not in sources_to_add:
                        sources_to_add[source_type].append(source)

        elif source_type == "Экзамен":
            with st.container(height=60, border=False):
                action = sac.tabs(
                    items=[sac.TabsItem("Добавить экзамен", "clipboard-plus"),
                           sac.TabsItem("Удалить экзамен", "clipboard-x")
                           ],
                    align='center',
                    use_container_width=True)

            if action == "Удалить экзамен":
                source = st.selectbox("Выберите экзамен", sources, index=None, placeholder="...")
                if st.button(f'Удалить экзамен "{source}"', use_container_width=True, disabled=source is None):
                    if source not in sources_to_delete:
                        sources_to_delete[source_type].append(source)

            elif action == "Добавить экзамен":
                source = st.text_input("Название экзамена")
                if st.button("Добавить", use_container_width=True, disabled=source is None):
                    if source not in sources_to_add:
                        sources_to_add[source_type].append(source)

    return {
        "source_type_idx": source_type_idx,
        "sources_to_delete": sources_to_delete,
        "sources_to_add": sources_to_add,
        "extras_to_delete": extras_to_delete,
        "extras_to_add": extras_to_add
    }


def configure_tags(tags: str,
                   init_tags_to_delete: list[str] | None = None,
                   init_tags_to_add: list[str] | None = None):
    actions = [
        {
            "label": "Добавить тег",
            "icon": "clipboard-plus"
        },
        {
            "label": "Удалить тег",
            "icon": "clipboard-x"
        }
    ]
    tags_to_delete = init_tags_to_delete if init_tags_to_delete else []
    tags_to_add = init_tags_to_add if init_tags_to_add else []
    with st.container():
        action_idx = sac.tabs(
            items=[sac.TabsItem(**param) for param in actions],
            align='center',
            return_index=True,
            use_container_width=True)

        if actions[action_idx]["label"] == 'Удалить тег':
            tag = st.selectbox("Выберите тег", tags, index=None, placeholder="...")
            if st.button(f'Удалить тег "{tag}"',
                         use_container_width=True,
                         disabled=tag is None):
                if tag not in tags_to_delete:
                    tags_to_delete.append(tag)
        elif actions[action_idx]["label"] == 'Добавить тег':
            tag = st.text_input("Новый тег")
            if st.button("Добавить", use_container_width=True):
                if tag not in tags_to_add:
                    tags_to_add.append(tag)

    return {
        "action_idx": action_idx,
        "tags_to_delete": tags_to_delete,
        "tags_to_add": tags_to_add
    }


def param_view(state: dict, topic: str, name: str, color: str = "green"):
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col2:
            st.markdown("###")
            if st.button("Очистить", key=f"clear_{name}", use_container_width=True):
                state[name].clear()
        with col1:
            st.markdown(*styling(topic, font_size=20, text_align="left"))
            if len(state.get(name, [])) > 0:
                for v in state.get(name, []):
                    st.markdown(f":{color}[{v}]")
            else:
                st.markdown(":orange[Нет элементов]")
    return state


def source_view(state: dict, name: str, name_extra: str, color: str = "green"):
    with st.container(border=True):
        st.markdown(*styling("Источники", font_size=20, text_align="left"))
        if len(state.get(name, {})) > 0:
            for (k, val), (k_extra, val_extra) in zip(state.get(name, {}).items(), state.get(name_extra, {}).items()):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        st.markdown("######")
                        if st.button("Очистить", key=f"clear_{name}_{k}", use_container_width=True):
                            state[name][k].clear()
                            state[name_extra][k].clear()
                    with col1:
                        st.markdown(*styling(k, font_size=16, text_align="left", tag="h6"))
                        if len(val) > 0:
                            for v in val:
                                st.markdown(f":{color}[{v}]")
                        if len(val_extra) > 0:
                            for n, v in val_extra:
                                st.markdown(f"{n} $\\to$ :{color}[{v}]")
                        if len(val) == 0 and len(val_extra) == 0:
                            st.markdown(":orange[Нет элементов]")
        else:
            st.markdown(":orange[Нет элементов]")
        return state


def configure_view(state: dict):
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.container(border=True):
            st.markdown(*styling("Для добавления"))
            state = param_view(state, "Темы", "topics_to_add")
            state = source_view(state, "sources_to_add", "extras_to_add")
            state = param_view(state, "Теги", "tags_to_add")

    with col2:
        with st.container(border=True):
            st.markdown(*styling("Для удаления"))
            state = param_view(state, "Темы", "topics_to_delete", color="red")
            state = source_view(state, "sources_to_delete", "extras_to_delete", color="red")
            state = param_view(state, "Теги", "tags_to_delete", color="red")
    return state


def configure_save(conn: Connection, state: dict):
    _, col, _ = st.columns([1, 1, 1])
    with col:
        if st.button("Внести изменения", use_container_width=True):
            with Session(conn.engine) as session:
                for topic in state.get("topics_to_delete", []):
                    subtopic = topic.split(' / ')[-1]
                    parent_topic = topic.split(' / ')[-2] if len(topic.split(' / ')) > 1 else None
                    parent_id = conn.scalars(select(TopicTree.id).where(TopicTree.name == parent_topic)).one_or_none()
                    session.query(TopicTree).filter(TopicTree.name == subtopic,
                                                    TopicTree.parent_id == parent_id).delete()
                for source_type, sources in state.get("sources_to_delete", {}).items():
                    type_id = conn.scalars(select(TaskSourceType).where(TaskSourceType.name == source_type)).one()
                    for source in sources:
                        session.query(TaskSource).filter(TaskSource.name == source,
                                                         TaskSource.type_id == type_id).delete()
                for source_type, extras in state.get("extras_to_delete", {}).items():
                    type_id = conn.scalars(select(TaskSourceType).where(TaskSourceType.name == source_type)).one()
                    for source, extra in extras:
                        source_id = conn.scalars(select(TaskSource.id).where(TaskSource.name == source,
                                                                             TaskSource.type_id == type_id)).one()
                        session.query(TaskSourceExtra).filter(TaskSourceExtra.extra == extra,
                                                              TaskSourceExtra.source_id == source_id).delete()
                for tag in state.get("tags_to_delete", []):
                    session.query(TaskTag).filter(TaskTag.name == tag).delete()

                for topic in state.get("topics_to_add", []):
                    parts = topic.split(' / ')
                    child = parts[-1]
                    if len(parts) > 1:
                        parent = parts[-2]
                    else:
                        parent = None
                    parent_id = conn.scalars(select(TopicTree.id).where(TopicTree.name == parent)).one_or_none()
                    session.add(TopicTree(subject_id=state.get("subject_id"),
                                          name=child,
                                          parent_id=parent_id))
                for source_type, sources in state.get("sources_to_add", {}).items():
                    type_id = conn.scalars(select(TaskSourceType).where(TaskSourceType.name == source_type)).one()
                    for source in sources:
                        session.add(TaskSource(name=source, type_id=type_id))
                for source_type, extras in state.get("extras_to_add", {}).items():
                    type_id = conn.scalars(select(TaskSourceType).where(TaskSourceType.name == source_type)).one()
                    for source, extra in extras:
                        source_id = conn.scalars(select(TaskSource.id).where(TaskSource.name == source,
                                                                             TaskSource.type_id == type_id)).one()
                        session.add(TaskSourceExtra(extra=extra, source_id=source_id))
                for tag in state.get("tags_to_add", []):
                    session.add(TaskTag(name=tag))
                session.commit()
            state.clear()
    return state
