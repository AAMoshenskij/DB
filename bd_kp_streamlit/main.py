import streamlit as st
import asyncio
from pages.admin import admin_dashboard
from pages.athlete import athlete_dashboard
from pages.user import view_competitions
from pages.coach import coach_dashboard
from authentication import sign_up, login
from settings import init_pool, close_pool
from logs import get_registration_logs


async def main():
    st.title("Сервис регистрации спортсменов на соревнования по плаванию")

    connection_pool = await init_pool()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False  # Инициализация флага

    if st.session_state.logged_in:
        await select_role(st.session_state.role_id, connection_pool)  # Если вход выполнен, показываем выбор роли 

        # Кнопка "Выход" размещена внизу
        if st.button("Выход"):
            st.session_state.logged_in = False  # Сбрасываем флаг авторизации
            st.session_state.role_id = None      # Сбрасываем ID роли (если требуется)
            st.stop()                            # Останавливаем выполнение текущего скрипта

    else:
        choice = st.radio("Выберите действие:", ["Вход", "Регистрация"])

        if choice == "Вход":
            role_id = await login(connection_pool)  # Добавлено await для асинхронного вызова
            if role_id:
                st.session_state.logged_in = True
                st.session_state.role_id = role_id  # Устанавливаем ID роли
                await select_role(role_id, connection_pool)
                await get_registration_logs(connection_pool) 
        elif choice == "Регистрация":
            role_id = await sign_up(connection_pool)  # Добавлено await для асинхронного вызова
            if role_id:
                st.session_state.logged_in = True
                st.session_state.role_id = role_id  # Устанавливаем ID роли
                await select_role(role_id, connection_pool)
                await get_registration_logs(connection_pool)

    await close_pool(connection_pool)

async def select_role(role_id, connection_pool):
    # Выбор роли и отображение соответствующей информации
    if role_id == 1:
        await admin_dashboard(connection_pool)
    elif role_id == 2:
        await coach_dashboard(st.session_state.user_id, connection_pool)
    elif role_id == 3:
        await athlete_dashboard(st.session_state.user_id, connection_pool)
    elif role_id == 4:
        await view_competitions(connection_pool)

if __name__ == "__main__":
    asyncio.run(main())  # Запускаем асинхронную функцию main



