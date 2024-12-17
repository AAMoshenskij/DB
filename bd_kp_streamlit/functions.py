#from settings import get_connection
import streamlit as st
from asyncpg import Record
from datetime import datetime

async def record_int(record, id_key):
    if isinstance(record, Record):
        # Проверяем, есть ли ключ id_key в Record
        id_without = id_key.strip("'")
        if id_without in record:
            return record[id_key]
        #else:
            #raise ValueError(f"Record does not contain '{id_key}' key")
    return record  # Если record не Record, возвращаем его как есть

async def get_teams(connection_pool):
    async with connection_pool.acquire() as conn:
        teams = await conn.fetch("SELECT team_id, team_name FROM Teams;")
    return teams

async def get_team_id(team_name, connection_pool):
    async with connection_pool.acquire() as conn:
        team_id = await conn.fetchrow("SELECT team_id FROM Teams WHERE team_name = $1", team_name)
    return team_id

async def add_coach(user_id, coach_name, team_id, connection_pool):
    async with connection_pool.acquire() as conn:
        try:
            # Добавление нового тренера в таблицу Coaches и получение coach_id
            if isinstance(team_id, Record):
                team_id = team_id['team_id']
            coach_id = await conn.fetchval("INSERT INTO Coaches (name, team_id, user_id) VALUES ($1, $2, $3) RETURNING coach_id;",
                                            coach_name, team_id, user_id)

            # Обновление массива coaches_ids
            await conn.execute("""
                UPDATE Teams
                SET coaches_ids = 
                    CASE 
                        WHEN coaches_ids IS NULL THEN ARRAY[$1]::integer[] 
                        ELSE array_append(coaches_ids, $1) 
                    END 
                WHERE team_id = $2;
            """, coach_id, team_id)
        except Exception as e:
            print(f"An error occurred: {e}")

async def get_coaches_for_team(team_id, connection_pool):
    async with connection_pool.acquire() as conn:
        coaches = await conn.fetch("SELECT coach_id, name FROM Coaches WHERE team_id = $1;", team_id)
    return coaches

async def get_coach_id_on_name(coach_name, connection_pool):
    async with connection_pool.acquire() as conn:
        coach_id = await conn.fetchrow("SELECT coach_id FROM Coaches WHERE name = $1", coach_name)
    return coach_id

async def add_athlete(user_id, athlete_name, date_of_birth, team_id, coach_id, rank, gender, connection_pool):
    async with connection_pool.acquire() as conn:
        if isinstance(date_of_birth, str):
            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        if isinstance(coach_id, Record):
            coach_id = coach_id['coach_id']
        await conn.execute("INSERT INTO Athletes (user_id, athlete_name, date_of_birth, team_id, coach_id, rank, gender) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                           user_id, athlete_name, date_of_birth, team_id, coach_id, rank, gender)

async def is_competition_to_be(competition_name, connection_pool):
    query = 'SELECT COUNT(*) FROM Competitions WHERE competition_name = $1;'
    result = await execute_query3(connection_pool, query, (competition_name,))
    
    if result is not None and len(result) > 0:
        return result[0][0] > 0
    return False

async def execute_query(connection_pool, query):
    async with connection_pool.acquire() as conn:
        try:
            results = await conn.fetch(query)
            return results
        except Exception as e:
            print(f"Ошибка во время выполнения запроса: {e}")
            return None


async def execute_query2(connection_pool, query, params=None):
    async with connection_pool.acquire() as conn:
        if params is not None:
            # Применяем record_int к каждому параметру с указанием ключа
            processed_params = []
            for param in params:
                try:
                    param_with = 'param'
                    processed_params.append(await record_int(param, param_with))
                except ValueError as e:
                    print(f"Error processing param {param}: {e}")
                    raise  # Перебрасываем исключение дальше
            result = await conn.fetch(query, *processed_params)  # Используем распаковку для передачи параметров
        else:
            result = await conn.fetch(query)
        return result  # Возвращаем результат


async def execute_query3(connection_pool, query, params=None):
    async with connection_pool.acquire() as conn:
        try:
            results = await conn.fetch(query, *params) if params else await conn.fetch(query)
            return results
        except Exception as e:
            print(f"Ошибка во время выполнения запроса: {e}")
            return None

async def add_competition(competition_name, competition_date, competition_place, distance_names, connection_pool):
    async with connection_pool.acquire() as conn:
        # Добавление соревнования
        competition_id = await conn.fetchval(
            "INSERT INTO Competitions (competition_name, competition_date, competition_place) VALUES ($1, $2, $3) RETURNING competition_id;",
            competition_name, competition_date, competition_place
        )
        #print(competition_id)
        # Добавление дистанций для соревнования
        for distance_name in distance_names:
            await conn.execute(
                "INSERT INTO Distances (competition_id, distance_name) VALUES ($1, $2)",
                competition_id, distance_name
            )

async def is_team_to_be(team_name, connection_pool):
    query = 'SELECT COUNT(*) FROM Teams WHERE team_name = $1;'
    result = await execute_query3(connection_pool, query, (team_name,))
    
    if result is not None and len(result) > 0:
        return result[0][0] > 0
    return False

async def add_team(team_name, connection_pool):
    async with connection_pool.acquire() as conn:
        await conn.execute("INSERT INTO Teams (team_name) VALUES ($1)", team_name)

async def get_competitions_for_athlete(connection_pool):
    async with connection_pool.acquire() as conn:
        competitions = await conn.fetch("SELECT competition_id, competition_name FROM Competitions;")
    return competitions

async def get_distances_for_athlete(competition_id, connection_pool):
    async with connection_pool.acquire() as conn:
        distances = await conn.fetch("SELECT distance_id, distance_name FROM Distances WHERE competition_id = $1;", competition_id)
    return distances

async def register_athlete_for_athlete(athlete_id, competition_id, distance_id, application_time, connection_pool):
    async with connection_pool.acquire() as conn:
        if isinstance(athlete_id, Record):
            athlete_id = athlete_id['athlete_id']
        if isinstance(competition_id, Record):
            competition_id = competition_id['competition_id']
        if isinstance(distance_id, Record):
            distance_id = distance_id['distance_id']
        if isinstance(application_time, Record):
            application_time = application_time['application_time']
        await conn.execute("""
            INSERT INTO Registrations (athlete_id, competition_id, distance_id, application_time) 
            VALUES ($1, $2, $3, $4);
        """, athlete_id, competition_id, distance_id, application_time)

async def get_athlete_id(user_id, connection_pool):
    async with connection_pool.acquire() as conn:
        athlete_id = await conn.fetchrow("SELECT athlete_id FROM Athletes WHERE user_id = $1", user_id)
    return athlete_id

async def is_athlete_registered_for_distance(athlete_id, competition_id, distance_id, connection_pool):
    query = 'SELECT COUNT(*) FROM Registrations WHERE athlete_id = $1 AND competition_id = $2 AND distance_id = $3;'
    if isinstance(athlete_id, Record):
        athlete_id = athlete_id['athlete_id']
    if isinstance(competition_id, Record):
        competition_id = competition_id['competition_id']
    if isinstance(distance_id, Record):
        distance_id = distance_id['distance_id']
    result = await execute_query2(connection_pool, query, (athlete_id, competition_id, distance_id))
    return result[0][0] > 0

async def count_registered_distances(athlete_id, competition_id, connection_pool):
    query = 'SELECT COUNT(*) FROM Registrations WHERE athlete_id = $1 AND competition_id = $2;'
    if isinstance(athlete_id, Record):
        athlete_id = athlete_id['athlete_id']
    if isinstance(competition_id, Record):
        competition_id = competition_id['competition_id']
    result = await execute_query2(connection_pool, query, (athlete_id, competition_id))
    return result[0][0]

async def get_coach_id(user_id, connection_pool):
    async with connection_pool.acquire() as conn:
        coach_id = await conn.fetchrow("SELECT coach_id FROM Coaches WHERE user_id = $1", user_id)
    return coach_id

async def get_athletes_for_coach(coach_id, connection_pool):
    async with connection_pool.acquire() as conn:
        if isinstance(coach_id, Record):
            coach_id = coach_id['coach_id']
        athletes = await conn.fetch("SELECT athlete_id, athlete_name FROM Athletes WHERE coach_id = $1;", coach_id)
    return athletes

async def get_coach_name(user_id, connection_pool):
    async with connection_pool.acquire() as conn:    
        coach_name = await conn.fetchrow("SELECT name FROM Coaches WHERE user_id = $1", user_id)
    return coach_name

async def get_athletes_registered(connection_pool):
    query = '''
    SELECT
        c.competition_name,
        d.distance_name,
        a.athlete_name,
        r.application_time,
        a.rank,
        a.gender,
        a.date_of_birth
    FROM
        Registrations r
    JOIN Competitions c ON r.competition_id = c.competition_id
    JOIN Distances d ON r.distance_id = d.distance_id
    JOIN Athletes a ON r.athlete_id = a.athlete_id
    WHERE
        r.application_time ~ '^[0-9]{1,2}:[0-9]{2}(\.[0-9]{1,2})?'
    ORDER BY
        c.competition_name,
        d.distance_name,
        TO_TIMESTAMP('00:' || r.application_time, 'HH24:MI:SS.MS');
    '''
    
    results = await execute_query(connection_pool, query)

    competitions = {}
    for competition_name, distance_name, athlete_name, application_time, rank, gender, date_of_birth in results:
        if competition_name not in competitions:
            competitions[competition_name] = {}
        if distance_name not in competitions[competition_name]:
            competitions[competition_name][distance_name] = {'male': [], 'female': []}

        competitions[competition_name][distance_name][gender].append({
            'athlete_name': athlete_name,
            'application_time': application_time,
            'rank': rank,
            'date_of_birth': date_of_birth
        })
    
    return competitions