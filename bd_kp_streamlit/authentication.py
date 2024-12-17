import streamlit as st
import re
import bcrypt
from datetime import datetime
from functions import get_teams, get_team_id, add_coach, get_coaches_for_team, get_coach_id_on_name, add_athlete
#from settings import get_connection

async def fetch_users(connection_pool):
    """Получает всех пользователей из базы данных."""
    async with connection_pool.acquire() as conn:  # Получаем соединение из пула
        try:
            users = await conn.fetch("SELECT username, email, password FROM Users;")
            return users
        except Exception as e:
            # Здесь вы можете заменить st.error() на логику обработки ошибок
            print(f"Error fetching users: {e}")
            return []

def hash_password(password):
    """Хэширует пароль с использованием bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def validate_email(email):
    """Проверяет действительность email."""
    pattern = r"^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
    return re.match(pattern, email) is not None

def validate_username(username):
    """Проверяет действительность имени пользователя."""
    pattern = r"^[a-zA-Z0-9]*$"
    return re.match(pattern, username) is not None

async def insert_user(email, username, password, connection_pool):
    """Вставляет пользователя в базу данных."""
    async with connection_pool.acquire() as conn:
        try:
            role_id = 4  # Пример, где 4 - посетитель
            user_id = await conn.fetchval("""
                INSERT INTO Users (username, password, email, role_id)
                VALUES ($1, $2, $3, $4) RETURNING user_id;
            """, username, password, email, role_id)
            return user_id
        except Exception as e:
            st.error(f"Error inserting user: {e}")

async def insert_coach(email, username, password, connection_pool):
    """Вставляет пользователя в базу данных."""
    async with connection_pool.acquire() as conn:
        try:
            role_id = 2  # Пример, где 2 - тренер
            user_id = await conn.fetchval("""
                INSERT INTO Users (username, password, email, role_id)
                VALUES ($1, $2, $3, $4) RETURNING user_id;
            """, username, password, email, role_id)
            return user_id
        except Exception as e:
            st.error(f"Error inserting user: {e}")

async def insert_athlete(email, username, password, connection_pool):
    """Вставляет пользователя в базу данных."""
    async with connection_pool.acquire() as conn:
        try:
            role_id = 3  # Пример, где 3 - спортсмен
            user_id = await conn.fetchval("""
                INSERT INTO Users (username, password, email, role_id)
                VALUES ($1, $2, $3, $4) RETURNING user_id;
            """, username, password, email, role_id)
            return user_id
        except Exception as e:
            st.error(f"Error inserting user: {e}")

async def authenticate_user(username, password, connection_pool):
    """Аутентификация пользователя."""
    async with connection_pool.acquire() as conn:    
        user = await conn.fetchrow("""
            SELECT user_id, password, role_id FROM Users WHERE username = $1;
        """, username)
    
        if user and check_password(user[1], password):
            return user[0], user[2]  # Возвращает user_id и role_id
        return None, None  # Возвращает None, если аутентификация не удалась

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def sign_up(connection_pool):
    """Регистрация нового пользователя."""
    #with st.form(key='signup', clear_on_submit=True):
    st.subheader(':green[Регистрация нового пользователя]')

        # Поля для ввода информации о пользователе
    email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
    username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
    password1 = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')
    password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Your Password', type='password')

    role = "Посетитель"

        # Кнопка отправки формы
    

    if st.button("Зарегистрироваться", key="register_competition"):
            # Проверка регистрации
        if email:
            if validate_email(email):
                users = await fetch_users(connection_pool)  # Получаем пользователей асинхронно
                if email not in [user[1] for user in users]:
                    if username not in [user[0] for user in users]:  
                        if validate_username(username):
                            if len(username) >= 2:
                                if len(password1) >= 6:
                                    if password1 == password2:
                                        # Вставка пользователя в базу данных с хэшированным паролем
                                        hashed_password = hash_password(password1)
                                        user_id = await insert_user(email, username, hashed_password, connection_pool)  # Передаем роль
                                        role_id = 1 if role == "Спортсмен" else 4
                                        st.session_state.logged_in = True  # Устанавливаем флаг входа
                                        st.session_state.role_id = role_id
                                        st.session_state.user_id = user_id
                                        st.success('Account created successfully!')
                                        st.balloons()
                                    else:
                                        st.warning('Passwords Do Not Match')
                                else:
                                    st.warning('Password is too Short')
                            else:
                                st.warning('Username Too short')
                        else:
                            st.warning('Invalid Username')
                    else:
                        st.warning('Пользователь с таким Username уже есть!')
                else:
                    st.warning('Пользователь с таким Email уже есть!')

async def sign_up_for_coach(connection_pool):
    """Регистрация нового пользователя."""
    #with st.form(key='signup', clear_on_submit=True):
    st.subheader(':green[Регистрация нового тренера]')

        # Поля для ввода информации о пользователе
    coach_name = st.text_input(':blue[Name]', placeholder='Enter Coach Name')
    email = st.text_input(':blue[Email]', placeholder='Enter Coach Email')
    username = st.text_input(':blue[Username]', placeholder='Enter Coach Username')
    password1 = st.text_input(':blue[Password]', placeholder='Enter Coach Password', type='password')
    password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Coach Password', type='password')

    teams = await get_teams(connection_pool)  # Получаем команды асинхронно
    team_names = [team[1] for team in teams]
    selected_team = st.selectbox("Выберите команду", team_names, key="select_competition")
    team_id = await get_team_id(selected_team, connection_pool)  # Получаем team_id асинхронно
    role = "Тренер"

    if st.button("Зарегистрировать тренера", key="register_coach"):
            # Проверка регистрации
        if email:
            if validate_email(email):
                users = await fetch_users(connection_pool)  # Получаем пользователей асинхронно
                if email not in [user[1] for user in users]:
                    if username not in [user[0] for user in users]:  
                        if validate_username(username):
                            if len(username) >= 2:
                                if len(password1) >= 6:
                                    if password1 == password2:
                                        hashed_password = hash_password(password1)
                                        user_id = await insert_coach(email, username, hashed_password, connection_pool)  # Передаем роль
                                        await add_coach(user_id, coach_name, team_id, connection_pool)  # Добавляем тренера асинхронно
                                        st.success('Account created successfully!')
                                        st.balloons()
                                    else:
                                        st.warning('Passwords Do Not Match')
                                else:
                                    st.warning('Password is too Short')
                            else:
                                st.warning('Username Too short')
                        else:
                            st.warning('Invalid Username')
                    else:
                        st.warning('Тренер с таким именем пользователя уже есть!')
                else:
                    st.warning('Тренер с таким email уже есть!')

async def sign_up_for_athlete(connection_pool):
    """Регистрация нового спортсмена."""
    st.subheader(':green[Регистрация нового спортсмена]')
    ranks = ["3 youth", "2 youth", "1 youth", "3", "2", "1", "CMS", "MS"]
    genders = ["male", "female"]

    # Поля для ввода информации о пользователе
    athlete_name = st.text_input(':blue[Name]', placeholder='Enter Athlete Name')
    rank = st.selectbox("Выберите разряд спортсмена", ranks, key="select_rank")
    gender = st.selectbox("Выберите пол", genders, key="select_gender")
    date_of_birth_input = st.text_input(':blue[date of birth]', placeholder='Enter date of birth')
    email = st.text_input(':blue[Email]', placeholder='Enter Coach Email')
    username = st.text_input(':blue[Username]', placeholder='Enter Coach Username')
    password1 = st.text_input(':blue[Password]', placeholder='Enter Coach Password', type='password')
    password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Coach Password', type='password')

    teams = await get_teams(connection_pool)  # Получаем команды асинхронно
    team_names = [t[1] for t in teams]
    selected_team = st.selectbox("Выберите соревнование", team_names, key="select_team")

    if selected_team:
        team_id = teams[team_names.index(selected_team)][0]
        coaches = await get_coaches_for_team(team_id, connection_pool)  # Получаем тренеров асинхронно
        coach_names = [coach[1] for coach in coaches]
        selected_coach = st.selectbox("Выберите тренера", coach_names, key="select_coach")

        if st.button("Зарегистрировать спортсмена", key="register_athlete"):
            # Проверка регистрации
            if email:
                if validate_email(email):
                    users = await fetch_users(connection_pool)  # Получаем пользователей асинхронно
                    if email not in [user[1] for user in users]:
                        if username not in [user[0] for user in users]:  
                            if validate_username(username):
                                if len(username) >= 2:
                                    if len(password1) >= 6:
                                        try:
                                            date_of_birth = datetime.strptime(date_of_birth_input, "%Y-%m-%d").date()
                                            if password1 == password2:
                                                # Вставка пользователя в базу данных с хэшированным паролем
                                                hashed_password = hash_password(password1)
                                                coach_id = await get_coach_id_on_name(selected_coach, connection_pool)  # Получаем coach_id асинхронно
                                                user_id = await insert_athlete(email, username, hashed_password, connection_pool)  # Передаем роль
                                                await add_athlete(user_id, athlete_name, date_of_birth, team_id, coach_id, rank, gender, connection_pool)  # Добавляем спортсмена асинхронно
                                                st.success('Account created successfully!')
                                                st.balloons()
                                            else:
                                                st.warning('Passwords Do Not Match')
                                        except ValueError:
                                            st.error("Неверный формат даты. Используйте формат YYYY-MM-DD.")
                                    else:
                                        st.warning('Password is too Short')
                                else:
                                    st.warning('Username Too short')
                            else:
                                st.warning('Invalid Username')
                        else:
                            st.warning('Спортсмен с таким именем пользователя уже есть!')
                    else:
                        st.warning('Спортсмен с таким email уже есть!')

async def login(connection_pool):
    """Функция для входа пользователя в систему."""
    username = st.text_input("Имя пользователя", key="login_username")
    password = st.text_input("Пароль", type='password', key="login_password")

    if st.button("Войти", key="login_button"):
        user_id, role_id = await authenticate_user(username, password, connection_pool)  # Аутентификация асинхронно
        if user_id:
            st.session_state.user_id = user_id  # Сохраняем айди в session_state
            st.session_state.role_id = role_id
            st.session_state.logged_in = True  # Устанавливаем флаг входа
            st.success("Вход выполнен!")
        else:
            st.error("Неверный логин или пароль")

