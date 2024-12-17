-- Таблица для хранения информации о пользователях сайта
CREATE TABLE Users (
       user_id SERIAL PRIMARY KEY,
       username VARCHAR(50) NOT NULL,
       password VARCHAR(255) NOT NULL,
       email VARCHAR(100) NOT NULL,
       role_id INT REFERENCES UserRoles(role_id)
);

COMMENT ON TABLE Users IS 'Информация о пользователях сайта';

COMMENT ON COLUMN Users.user_id IS 'Уникальный идентификатор пользователя';

COMMENT ON COLUMN Users.username IS 'Логин пользователя';

COMMENT ON COLUMN Users.password IS 'Пароль пользователя';

COMMENT ON COLUMN Users.email IS 'Email пользователя';

COMMENT ON COLUMN Users.role_id IS 'Роль пользователя';

-- Таблица для хранения информации о ролях пользователей
CREATE TABLE UserRoles (
       role_id SERIAL PRIMARY KEY,
       role_name VARCHAR(50) NOT NULL UNIQUE
);

COMMENT ON TABLE UserRoles IS 'Информация о ролях пользователей сайта';

COMMENT ON COLUMN UserRoles.role_id IS 'Уникальный идентификатор пользователя';

COMMENT ON COLUMN UserRoles.role_name IS 'Название роли';

-- Таблица для хранения информации о спортсменах
CREATE TABLE Athletes (
       athlete_id SERIAL PRIMARY KEY,
       user_id INT REFERENCES Users(user_id),
       athlete_name VARCHAR(50) NOT NULL,
       date_of_birth DATE,
       team_id INT REFERENCES Teams(team_id),
       coach_id INT NOT NULL,
       rank VARCHAR(50) NOT NULL,
       gender VARCHAR(6) NOT NULL
);

COMMENT ON TABLE Athletes IS 'Информация о спортсменах';

COMMENT ON COLUMN Athletes.athlete_id IS 'Уникальный идентификатор спортсмена';

COMMENT ON COLUMN Athletes.user_id IS 'Уникальный идентификатор пользователя-спортсмена';

COMMENT ON COLUMN Athletes.name IS 'Имя спортсмена';

COMMENT ON COLUMN Athletes.user_id IS 'Дата рождения спортсмена';

COMMENT ON COLUMN Athletes.team_id IS 'Команда спортсмена';

COMMENT ON COLUMN Athletes.coach_id IS 'Тренер спортсмена';

-- Таблица для хранения информации о зарегистрированных спортсменах
CREATE TABLE Registrations (
       registration_id SERIAL PRIMARY KEY,
       athlete_id INT REFERENCES Athletes(athlete_id),
       competition_id INT REFERENCES Competitions(competition_id),
       distance_id INT REFERENCES Distances(distance_id),
       application_time VARCHAR(8)
);

COMMENT ON TABLE Registrations IS 'Информация о зарегистрированных спортсменах';

COMMENT ON COLUMN Registrations.registration_id IS 'Уникальный идентификатор регистрации спортсмена';

COMMENT ON COLUMN Registrations.athlete_id IS 'Уникальный идентификатор спортсмена';

COMMENT ON COLUMN Registrations.competition_id IS 'Уникальный идентификатор соревнования';

-- Таблица для хранения информации о соревнованиях
CREATE TABLE Competitions (
       competition_id SERIAL PRIMARY KEY,
       competition_name VARCHAR(100) NOT NULL,
       competition_date DATE NOT NULL
       competition_place VARCHAR(50)
);

COMMENT ON TABLE Competitions IS 'Информация о соревнованиях';

COMMENT ON COLUMN Competitions.competition_id IS 'Уникальный идентификатор соревнования';

COMMENT ON COLUMN Competitions.competition_name IS 'Название соревнования';

COMMENT ON COLUMN Competitions.competition_date IS 'Дата проведения соревнования';

COMMENT ON COLUMN Competitions.location IS 'Место проведения соревнования';

-- Таблица для хранения информации о дистанциях соревнований 
CREATE TABLE Distances (
       distance_id SERIAL PRIMARY KEY,
       competition_id INT REFERENCES Competitions(competition_id),
       distance_name VARCHAR(100) NOT NULL,
       distance INT NOT NULL
);

COMMENT ON TABLE Distances IS 'Информация о дистанциях соревнований';

COMMENT ON COLUMN Distances.distance_id IS 'Уникальный идентификатор дистанции';

COMMENT ON COLUMN Distances.distance_id IS 'Уникальный идентификатор соревнования';

COMMENT ON COLUMN Distances.distance_name IS 'Название дистанции';

COMMENT ON COLUMN Distances.distance IS 'Дистанция';

CREATE TABLE Teams (
       team_id SERIAL PRIMARY KEY,
       team_name VARCHAR(100) NOT NULL,
       coaches_ids INT
);

COMMENT ON TABLE Teams IS 'Информация о командах';

COMMENT ON COLUMN Teams.team_id IS 'Уникальный идентификатор команды';

COMMENT ON COLUMN Teams.team_name IS 'Название команды';

-- Таблица для хранения информации о тренерах
CREATE TABLE Coaches (
       coach_id SERIAL PRIMARY KEY,
       name VARCHAR(100) NOT NULL,
       team_id INT REFERENCES Teams(team_id)
);

COMMENT ON TABLE Coaches IS 'Информация о тренерах';

COMMENT ON COLUMN Coaches.coach_id IS 'Уникальный идентификатор тренера';

COMMENT ON COLUMN Coaches.name IS 'Имя тренера тренера';

COMMENT ON COLUMN Coaches.team_id IS 'Уникальный идентификатор команды тренера';

-- Создание таблицы для логов
CREATE TABLE RegistrationLogs (
    log_id SERIAL PRIMARY KEY,
    registration_id INT NOT NULL,
    action VARCHAR(10) NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMP DEFAULT NOW()
);

-- Создание функции для триггера
CREATE OR REPLACE FUNCTION log_registration_changes() 
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO RegistrationLogs(registration_id, action, new_data)
        VALUES (NEW.registration_id, 'INSERT', row_to_json(NEW));
        RETURN NEW;
    
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO RegistrationLogs(registration_id, action, old_data, new_data)
        VALUES (OLD.registration_id, 'UPDATE', row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO RegistrationLogs(registration_id, action, old_data)
        VALUES (OLD.registration_id, 'DELETE', row_to_json(OLD));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера
CREATE TRIGGER registration_changes
AFTER INSERT OR UPDATE OR DELETE ON Registrations
FOR EACH ROW
EXECUTE FUNCTION log_registration_changes();

