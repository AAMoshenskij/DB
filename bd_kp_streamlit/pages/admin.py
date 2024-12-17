import streamlit as st
#from db import add_competition, is_competition_to_be, is_team_to_be, add_team
from datetime import datetime
#from dependancies import sign_up_for_coach, sign_up_for_athlete
from functions import is_competition_to_be, add_competition, is_team_to_be, add_team
from authentication import sign_up_for_coach, sign_up_for_athlete

import streamlit as st
from datetime import datetime

distances = [
    "50m Butterfly", "100m Butterfly", "200m Butterfly",
    "50m Backstroke", "100m Backstroke", "200m Backstroke",
    "50m Breaststroke", "100m Breaststroke", "200m Breaststroke",
    "50m Freestyle", "100m Freestyle", "200m Freestyle",
    "400m Freestyle", "800m Freestyle", "1500m Freestyle",
    "100m Complex", "200m Complex", "400m Complex"
]

async def admin_dashboard(connection_pool):
    st.header("Панель администратора")

    choice = st.radio("Выберите действие:", ["Добавить соревнование", "Добавить команду", "Добавить тренера", "Добавить спортсмена"])

    if choice == "Добавить соревнование":
        st.subheader(':green[Добавление нового соревнования]')
        
        competition_name = st.text_input("Официальное название соревнований", key="competition_name")
        competition_date_input = st.text_input("Дата проведения соревнований (в формате YYYY-MM-DD)", key="competition_date")
        competition_place = st.text_input("Место проведения соревнований", key="competition_place")

        # Инициализация списка дистанций в сессии
        if 'competition_distances' not in st.session_state:
            st.session_state.competition_distances = []
            # Добавляем две обязательные дистанции
            st.session_state.competition_distances.append(distances[0])  # По умолчанию первая дистанция
            st.session_state.competition_distances.append(distances[1])  # По умолчанию вторая дистанция

        # Отображение обязательных дистанций
        for i in range(2):
            distance = st.session_state.competition_distances[i]
            selected_distance = st.selectbox(
                f"Выберите дистанцию",
                distances,
                index=distances.index(distance),
                key=f"select_distance_obligatory_{i}"  # Уникальный ключ для обязательных дистанций
            )
            st.session_state.competition_distances[i] = selected_distance  # Обновление состояния

        # Отображение дополнительных дистанций
        distances_changed = False  # Флаг для отслеживания изменений дистанций
        for i in range(2, len(st.session_state.competition_distances)):
            selected_distance = st.selectbox(
                f"Выберите дистанцию",
                distances,
                index=distances.index(st.session_state.competition_distances[i]),
                key=f"select_distance_{i}"  # Уникальный ключ для дополнительных дистанций
            )
            if selected_distance != st.session_state.competition_distances[i]:
                st.session_state.competition_distances[i] = selected_distance
                distances_changed = True  # Установка флага изменения

            # Кнопка для удаления дистанции
            if st.button(f"Удалить дистанцию", key=f"remove_distance_{i}"):
                st.session_state.competition_distances.pop(i)  # Удаляем выбранную дистанцию
                distances_changed = True  # Установка флага изменения

                break  # Прерываем цикл для обновления состояния

        # Проверяем, были ли изменения в дистанциях и обновляем отображение
        if distances_changed:
            # Обновляем список, чтобы отобразить изменения
            st.session_state.competition_distances = st.session_state.competition_distances

        # Кнопка для добавления новой дистанции (не больше 16 дополнительных)
        if len(st.session_state.competition_distances) < 18:  # 2 обязательные + 16 дополнительных
            if st.button("Добавить дистанцию"):
                st.session_state.competition_distances.append(distances[2])  # Добавляем новую дистанцию по умолчанию

        # Кнопка для добавления соревнования
        if st.button("Добавить соревнование"):
            if not competition_name or not competition_date_input or not competition_place:
                st.error("Все поля должны быть заполнены.")
            elif len(st.session_state.competition_distances) != len(set(st.session_state.competition_distances)):
                st.error("Ошибка: все дистанции должны быть уникальными.")
            else:
                # Проверка формата даты
                try:
                    competition_date = datetime.strptime(competition_date_input, "%Y-%m-%d").date()

                    # Проверка, существует ли уже такое соревнование
                    if await is_competition_to_be(competition_name, connection_pool):
                        st.error("Соревнование с таким названием уже существует.")
                    else:
                        # Если все проверки пройдены, вызываем функцию добавления соревнования
                        await add_competition(competition_name, competition_date, competition_place, st.session_state.competition_distances, connection_pool)
                        st.success("Соревнование успешно добавлено!")
                except ValueError:
                    st.error("Неверный формат даты. Используйте формат YYYY-MM-DD.")



    if choice == "Добавить команду":
        st.subheader(':green[Добавление новой команды]')
        
        team_name = st.text_input("Название команды", key="team_name")

        if st.button("Добавить команду"):
            if not team_name:
                st.error("Поле должно быть заполнено.")
            else:
                    # Проверка, существует ли уже такое соревнование
                    if await is_team_to_be(team_name, connection_pool):
                        st.error("Команда с таким названием уже существует.")
                    else:
                        # Если все проверки пройдены, вызываем функцию добавления соревнования
                        await add_team(team_name, connection_pool)
                        st.success("Команда успешно добавлена!")

    if choice == "Добавить тренера":
        
        await sign_up_for_coach(connection_pool)

    if choice == "Добавить спортсмена":
        
        await sign_up_for_athlete(connection_pool)