import streamlit as st
#from db import get_competitions_for_athlete, get_distances_for_athlete, register_athlete_for_athlete, is_athlete_registered_for_distance, count_registered_distances, get_coach_id, get_athletes_for_coach, get_coach_name
import re
from functions import get_competitions_for_athlete, get_distances_for_athlete, register_athlete_for_athlete, is_athlete_registered_for_distance, count_registered_distances, get_coach_id, get_athletes_for_coach, get_coach_name

async def coach_dashboard(user_id, connection_pool):
    # Получаем coach_id на основе user_id
    coach_id = await get_coach_id(user_id, connection_pool)  # Функция, чтобы получить coach_id по user_id
    coach_name = await get_coach_name(user_id, connection_pool)
    #coach_name = coach_name_tuple[0]

    st.header("Панель тренера")
    
    st.write("Добро пожаловать, ", coach_name['name'])

    # Получаем спортсменов, которых тренирует тренер
    athletes = await get_athletes_for_coach(coach_id, connection_pool)  # Возвращает список спортсменов, которых тренирует этот тренер
    athlete_names = [athlete[1] for athlete in athletes]
    selected_athlete = st.selectbox("Выберите спортсмена", athlete_names, key="select_athlete")

    if selected_athlete:
        # Получаем athlete_id для выбранного спортсмена по их имени
        athlete_id = athletes[athlete_names.index(selected_athlete)][0]

        competitions = await get_competitions_for_athlete(connection_pool)  # Функция, чтобы получить соревнования
        competition_names = [comp[1] for comp in competitions]
        selected_competition = st.selectbox("Выберите соревнование", competition_names, key="select_competition")

        if selected_competition:
            competition_id = competitions[competition_names.index(selected_competition)][0]
            distances = await get_distances_for_athlete(competition_id, connection_pool)
            distance_names = [dist[1] for dist in distances]
            selected_distance = st.selectbox("Выберите дистанцию", distance_names, key="select_distance")

            # Изменяем ввод времени на MM:SS.HH
            application_time = st.text_input("Введите заявочное время в формате MM:SS.HH (min:sec.hun)", key="application_time")

            if st.button("Зарегистрировать спортсмена на соревнование", key="register_competition"):
                # Проверка формата времени
                if await validate_time_format(application_time):
                    distance_id = distances[distance_names.index(selected_distance)][0]
                    # Проверяем, зарегистрирован ли спортсмен на эту дистанцию
                    if await is_athlete_registered_for_distance(athlete_id, competition_id, distance_id, connection_pool):
                        st.error("Спортсмен уже зарегистрирован на эту дистанцию.")
                    else:
                        # Проверка общего числа зарегистрированных дистанций
                        if await count_registered_distances(athlete_id, competition_id, connection_pool) >= 2:
                            st.error("Спортсмен не может зарегистрироваться более чем на две дистанции на одних соревнованиях.")
                        else:
                            # Регистрируем спортсмена
                            await register_athlete_for_athlete(athlete_id, competition_id, distance_id, application_time, connection_pool)
                            st.success(f"Спортсмен {selected_athlete} зарегистрирован на соревнование!")
                else:
                    st.error("Неверный формат времени. Пожалуйста, введите время в формате MM:SS.HH.")



async def validate_time_format(time_string):
    """Проверяет, соответствует ли строка формату MM:SS.HH."""
    # Формат: MM:SS.HH (например, 01:30.50)
    pattern = re.compile(r'^[0-5][0-9]:[0-5][0-9]\.[0-9]{2}$')
    return bool(pattern.match(time_string))