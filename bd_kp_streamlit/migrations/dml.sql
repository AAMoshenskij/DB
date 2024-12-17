INSERT INTO UserRoles (role_name) VALUES
('Admin'),
('Coach'),
('Athlete'),
('Spectator');

INSERT INTO Users (username, password, email, role_id) VALUES
('admin_user', 'hashed_password_1', 'admin@example.com', 1),
('coach_user', 'hashed_password_2', 'coach@example.com', 2),
('athlete_user', 'hashed_password_3', 'athlete@example.com', 3),
('spectator_user', 'hashed_password_4', 'spectator@example.com', 4);

INSERT INTO Coaches (name, team_id) VALUES
('Coach A', 1),
('Coach B', 1),
('Coach C', 2);

INSERT INTO Teams (team_name, coaches_ids) VALUES
('Team Alpha', 1),
('Team Beta', 2);

INSERT INTO Athletes (user_id, name, date_of_birth, team_id, coach_id) VALUES
(3, 'John Doe', '2000-05-15', 1, 1),
(4, 'Jane Smith', '2002-08-22', 1, 1),
(5, 'Jim Brown', '1999-03-10', 2, 2);

INSERT INTO Competitions (competition_name, competition_date, location) VALUES
('Summer Swimming Championship', '2023-07-10', 'Pool A'),
('Winter Swimming Championship', '2023-12-15', 'Pool B');

INSERT INTO Distances (competition_id, distance_name, distance) VALUES
(1, '100m Freestyle', 100),
(1, '200m Butterfly', 200),
(2, '50m Freestyle', 50),
(2, '1500m Freestyle', 1500);

INSERT INTO Registrations (athlete_id, competition_id) VALUES
(1, 1),
(2, 1),
(3, 2);