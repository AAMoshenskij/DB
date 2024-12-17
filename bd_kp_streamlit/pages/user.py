import pandas as pd
import streamlit as st
from functions import get_athletes_registered


async def view_competitions(connection_pool):
    st.header("Доступные соревнования")
    athletes_data = await get_athletes_registered(connection_pool)
    
    if athletes_data:
        for competition_name, distances in athletes_data.items():
            st.subheader(competition_name)
            for distance_name, athletes in distances.items():
                st.write("")  # Разделитель между дистанциями
                st.markdown(f"Дистанция: {distance_name}")

                # Создаем таблицы для мужчин и женщин
                for gender in ['male', 'female']:
                    st.markdown(f"**{gender.capitalize()}**")  # Заголовок таблицы
                    table_data = []
                    
                    for athlete in athletes[gender]:
                        athlete_name = athlete['athlete_name']

                        application_time = athlete['application_time']
                        rank = athlete['rank']
                        date_of_birth = athlete['date_of_birth']
                        
                        # Удаляем ведущие нули перед выводом (например, `00:57:45.12` -> `57:45.12`)
                        if application_time.startswith('00:'):
                            application_time = application_time[3:]

                        year_of_birth = date_of_birth.year
                        # Добавляем строку в таблицу
                        table_data.append({
                            'Имя спортсмена': athlete_name,
                            'Заявочное время': application_time,
                            'Разряд': rank,
                            'Год рождения': year_of_birth
                        })
                    
                    # Преобразуем список в DataFrame и отображаем
                    if table_data:  # Проверяем, есть ли данные для отображения
                        df = pd.DataFrame(table_data)
                        st.table(df)
                    else:
                        st.write("Нет зарегистрированных спортсменов.")
    else:
        st.write("Нет зарегистрированных спортсменов.")










