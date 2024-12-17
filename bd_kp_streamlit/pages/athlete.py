import streamlit as st
#from db import get_competitions_for_athlete, get_distances_for_athlete, register_athlete_for_athlete, get_athlete_id, is_athlete_registered_for_distance, count_registered_distances
import re
from functions import get_competitions_for_athlete, get_distances_for_athlete, register_athlete_for_athlete, get_athlete_id, is_athlete_registered_for_distance, count_registered_distances


async def athlete_dashboard(user_id, connection_pool):
    athlete_id = await get_athlete_id(user_id, connection_pool)

    st.header("Панель спортсмена")
    
    competitions = await get_competitions_for_athlete(connection_pool)
    competition_names = [comp[1] for comp in competitions]
    selected_competition = st.selectbox("Выберите соревнование", competition_names, key="select_competition")

    if selected_competition:
        competition_id = competitions[competition_names.index(selected_competition)][0]
        distances = await get_distances_for_athlete(competition_id, connection_pool)
        distance_names = [dist[1] for dist in distances]
        selected_distance = st.selectbox("Выберите дистанцию", distance_names, key="select_distance")

        # Изменяем ввод времени на MM:SS.HH
        application_time = st.text_input("Введите заявочное время в формате MM:SS.HH (min:sec.hun)", key="application_time")

        if st.button("Зарегистрироваться на соревнование", key="register_competition"):
            # Проверка формата времени
            if await validate_time_format(application_time):
                # Добавляем "00:" к введенному времени
                #print(application_time)
                #application_time = f"00:{application_time}"  # Преобразование в формат HH:MM:SS.HH
                #print(application_time)

                distance_id = distances[distance_names.index(selected_distance)][0]

                # Проверяем, зарегистрирован ли спортсмен на эту дистанцию
                if await is_athlete_registered_for_distance(athlete_id, competition_id, distance_id, connection_pool):
                    st.error("Вы уже зарегистрированы на эту дистанцию.")
                else:
                    # Проверка общего числа зарегистрированных дистанций
                    if await count_registered_distances(athlete_id, competition_id, connection_pool) >= 2:
                        st.error("Вы не можете зарегистрироваться более чем на две дистанции на одних соревнованиях.")
                    else:
                        # Регистрируем спортсмена
                        await register_athlete_for_athlete(athlete_id, competition_id, distance_id, application_time, connection_pool)
                        st.success("Вы зарегистрированы на соревнование!")
            else:
                st.error("Неверный формат времени. Пожалуйста, введите время в формате MM:SS.HH.")


async def validate_time_format(time_string):
    """Проверяет, соответствует ли строка формату MM:SS.HH."""
    # Формат: MM:SS.HH (например, 01:30.50)
    pattern = re.compile(r'^[0-5][0-9]:[0-5][0-9]\.[0-9]{2}$')
    return bool(pattern.match(time_string))



