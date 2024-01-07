import random
import re
import time
from datetime import date

from typing import Tuple

import streamlit as st
from dateutil.relativedelta import relativedelta
from extra_streamlit_components.CookieManager import CookieManager
from sqlalchemy import Engine, select

from db.general_tables import User, Subject, School, Region
from pages.utils import send_verification_code


def first_name_input(cookie_manager: CookieManager, success_count: int) -> Tuple[str | None, int]:
    with st.container(border=True):
        cookie_name = "first_name"

        first_name = st.text_input(label="Имя",
                                   value=cookie_manager.get(cookie_name),
                                   placeholder="Иван",
                                   max_chars=15)
        if first_name:
            if first_name != cookie_manager.get(cookie_name):
                cookie_manager.set(
                    cookie=cookie_name,
                    val=first_name,
                    key="registration"
                )
            else:
                if not re.fullmatch('[а-яА-Я]+', first_name):
                    st.error("Имя должно состоять из букв русского алфавита", icon="❌")
                elif not first_name.capitalize() == first_name:
                    st.error("Имя должно начинаться с заглавной буквы", icon="❌")
                else:
                    st.success("Отлично!", icon="✅")
                    success_count += 1

    return first_name, success_count


def last_name_input(cookie_manager: CookieManager, success_count: int) -> Tuple[str | None, int]:
    with st.container(border=True):
        cookie_name = "last_name"

        last_name = st.text_input(label="Фамилия",
                                  value=cookie_manager.get(cookie_name),
                                  placeholder="Иванов",
                                  max_chars=15)
        if last_name:
            if last_name != cookie_manager.get(cookie_name):
                cookie_manager.set(
                    cookie=cookie_name,
                    val=last_name,
                    key="registration"
                )
            else:
                if not re.fullmatch('[а-яА-Я]+', last_name):
                    st.error("Фамилия должна состоять из букв русского алфавита", icon="❌")
                elif not last_name.capitalize() == last_name:
                    st.error("Фамилия должна начинаться с заглавной буквы", icon="❌")
                else:
                    st.success("Отлично!", icon="✅")
                    success_count += 1

    return last_name, success_count


def birth_date_input(cookie_manager: CookieManager, success_count: int) -> Tuple[str | None, int]:
    with st.container(border=True):
        cookie_name = "birth_date"

        cookie_val = cookie_manager.get(cookie_name)
        year, month, day = cookie_val.split(".")[::-1] if cookie_val else ("", "", "")

        if year.isnumeric() and month.isnumeric() and day.isnumeric():
            dt = date(int(year), int(month), int(day))
        else:
            dt = None

        birth_date = st.date_input(label="Дата рождения",
                                   value=dt,
                                   format="DD.MM.YYYY")

        if birth_date:
            if birth_date.strftime("%d.%m.%Y") != cookie_manager.get(cookie_name):
                cookie_manager.set(
                    cookie=cookie_name,
                    val=birth_date.strftime("%d.%m.%Y"),
                    key="registration"
                )
            else:
                if birth_date > date.today() - relativedelta(years=18):
                    st.error("Вам должно быть больше 18 лет", icon="❌")
                else:
                    st.success("Отлично!", icon="✅")
                    success_count += 1

    return birth_date, success_count


def personal_info_input(cookie_manager: CookieManager,
                        success_count: int) -> Tuple[str | None, str | None, str | None, int]:
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        first_name, success_count = first_name_input(cookie_manager, success_count)

    with col2:
        last_name, success_count = last_name_input(cookie_manager, success_count)

    with col3:
        birth_date, success_count = birth_date_input(cookie_manager, success_count)

    return first_name, last_name, birth_date, success_count


def email_input(cookie_manager: CookieManager, engine: Engine, success_count: int) -> Tuple[str | None, int]:
    if 'send_email' not in st.session_state:
        st.session_state.send_email = False

    if 'valid_email' not in st.session_state:
        st.session_state.valid_email = False

    if 'verified_email' not in st.session_state:
        st.session_state.verified_email = False

    if 'start_time' in st.session_state:
        delta = time.time() - st.session_state.start_time
        if delta > 60 and not st.session_state.verified_email:
            st.session_state.send_email = False
            st.session_state.pop('start_time')

    with st.container(border=True):
        col1, col2 = st.columns([4, 5])
        with col1:
            cookie_name = "email"

            email = st.text_input(label="Адрес электронной почты",
                                  value=cookie_manager.get(cookie_name),
                                  placeholder="example@test.com",
                                  disabled=st.session_state.verified_email,
                                  max_chars=30)
            if email:
                if email != cookie_manager.get(cookie_name):
                    cookie_manager.set(
                        cookie=cookie_name,
                        val=email,
                        key="registration"
                    )
                else:
                    if not re.fullmatch(r'[0-9A-Za-z_.]+@[0-9A-Za-z_.]+.[0-9A-Za-z_]+', email):
                        st.error("Неверный формат email", icon="❌")
                    elif len(engine.connect().scalars(select(User).where(User.email == email)).all()) != 0:
                        st.error("Пользователь с таким email уже существует", icon="❌")
                    else:
                        st.success("Отлично!", icon="✅")
                        st.session_state.valid_email = True
        with col2:
            col2_1, col2_2 = st.columns([1, 1])
            with col2_1:
                input_code = st.text_input(label="Код из письма",
                                           placeholder="12345",
                                           disabled=not st.session_state.valid_email or
                                                    not st.session_state.send_email or
                                                    st.session_state.verified_email)
            with col2_2:
                if not st.session_state.send_email:
                    st.subheader('')
                    if st.button("Отправить код",
                                 disabled=not st.session_state.valid_email,
                                 use_container_width=True):
                        st.session_state.start_time = time.time()
                        st.session_state.generated_code = random.randint(10000, 99999)
                        send_verification_code(email, st.session_state.generated_code)
                        st.session_state.send_email = True
                        cookie_manager.set(
                            cookie=cookie_name,
                            val=email,
                            key="registration"
                        )
                        time.sleep(0.01)
                else:
                    st.subheader('')
                    if st.button("Подтвердить код", disabled=st.session_state.verified_email):
                        if input_code == str(st.session_state.generated_code):
                            st.session_state.verified_email = True
                            cookie_manager.set(
                                cookie=cookie_name,
                                val=email,
                                key="registration"
                            )
                            time.sleep(0.01)
                with col2:
                    if st.session_state.verified_email and st.session_state.send_email:
                        st.success("Почта подтверждена!", icon="✅")
                        success_count += 1
                    elif not st.session_state.verified_email and st.session_state.send_email and len(input_code) == 0:
                        st.info("Код успешно отправлен на почту", icon="ℹ️")
                    elif not st.session_state.verified_email and st.session_state.send_email:
                        seconds_left = round(60 - time.time() + st.session_state.start_time)
                        st.error(f"Неверный код. Повторная отправка доступна через {seconds_left} сек", icon="❌")
                    elif email:
                        st.info("Отправьте код для подтверждения почты", icon="ℹ️")

    return email, success_count


def subject_input(engine: Engine, success_count: int) -> Tuple[str | None, int]:
    with st.container(border=True):
        subject = st.selectbox(label="Предмет",
                               placeholder="Выберите предмет",
                               options=engine.connect().scalars(
                                   select(Subject.name)).all(),
                               index=None)
        if subject:
            success_count += 1

    return subject, success_count


def grade_input(success_count: int) -> Tuple[str | None, int]:
    with st.container(border=True):
        grade = st.selectbox(label="Класс",
                             placeholder="5-11",
                             options=list(range(5, 12)),
                             index=None)
        if grade:
            success_count += 1

    return grade, success_count


def region_school_input(engine: Engine, success_count: int) -> Tuple[str | None, str | None, int]:
    col1, col2 = st.columns([1, 2])

    with col1:
        with st.container(border=True):
            region = st.selectbox(label="Регион",
                                  placeholder="Выберите регион",
                                  options=engine.connect().scalars(select(Region.name)).all(),
                                  index=None)
            if region:
                success_count += 1

    with col2:
        with st.container(border=True):
            school = st.selectbox(label="Школа",
                                  placeholder="Выберите школу",
                                  options=engine.connect().scalars(
                                      select(School.name)
                                      .join(Region, School.region_id == Region.id)
                                      .where(Region.name == region)).all(),
                                  disabled=not region,
                                  index=None)
            if school:
                success_count += 1

    return region, school, success_count


def password_input(success_count: int) -> Tuple[str | None, int]:
    with st.container(border=True):
        valid_password = False
        password = st.text_input(label="Пароль",
                                 placeholder="Введите пароль...",
                                 type="password")
        if password:
            if not re.fullmatch(r'[0-9A-Za-z_.-]+', password):
                st.error("Пароль должен состоять из букв латинского алфавита, цифр и '_', '.', '-'", icon="❌")
            elif len(password) < 8:
                st.error("Пароль должен состоять минимум из 8 символов", icon="❌")
            elif not bool(re.search(r'[0-9]', password)):
                st.error("Пароль должен содержать минимум 1 цифру", icon="❌")
            elif not bool(re.search(r'[A-Z]', password)):
                st.error("Пароль должен содержать минимум 1 заглавную букву", icon="❌")
            elif not bool(re.search(r'[a-z]', password)):
                st.error("Пароль должен содержать минимум 1 строчную букву", icon="❌")
            else:
                st.success("Отлично!", icon="✅")
                valid_password = True

    with st.container(border=True):
        password_2 = st.text_input(label="Повторите пароль",
                                   type="password",
                                   placeholder="Введите пароль...",
                                   disabled=not valid_password)
        if password != password_2:
            if len(password_2) > 0:
                st.error("Пароли не совпадают", icon="❌")
        else:
            if len(password_2) > 0:
                st.success("Отлично!", icon="✅")
                success_count += 1

    return password, success_count


def avatar_input(success_count: int):
    with st.container(border=True):
        avatar = st.selectbox(
            label="Аватар",
            placeholder="Выберите аватар...",
            options=['😀', '😅', '😇', '😎', '🤩', '🧐', '🥳', '🤗',
                     '😍', '🥹', '🙃', '🤓', '😌', '🤯', '🤔', '😏'])
        st.write("Выбранный аватар:")
        st.markdown(f'<p style="text-align: center;font-size: 108px;">{avatar}</p>',
                    unsafe_allow_html=True)

    return avatar, success_count
