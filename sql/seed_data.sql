BEGIN;

-- SYSTEM SETUP
-- The users Table:
INSERT INTO users (display_name, email) VALUES
('Samuel J. Ellis', 'samuel@whitelinegroup.com.au');


-- The organisations Table:
WITH organisations_data (organisation_name, time_zone, country_code) AS (
    VALUES
        ('Kilsyth Basketball Association', 'AEST', 'AU')
)
INSERT INTO organisations (organisation_name, time_zone, country_code, created_by_user_id)
SELECT
    od.organisation_name,
    od.time_zone,
    od.country_code,
    u.user_account_id AS created_by_user_id
FROM organisations_data od
JOIN users u ON u.email = 'samuel@whitelinegroup.com.au';


-- The user_permissions Table:
WITH user_permissions_data (email, can_schedule, can_approve, can_export) AS (
    VALUES
        ('samuel@whitelinegroup.com.au', TRUE, TRUE, TRUE)
)
INSERT INTO user_permissions (user_account_id, organisation_id, can_schedule, can_approve, can_export)
SELECT
    u.user_account_id,
    o.organisation_id,
    upd.can_schedule,
    upd.can_approve,
    upd.can_export
FROM user_permissions_data upd
JOIN users u ON u.email = upd.email
JOIN organisations o ON o.organisation_name = 'Kilsyth Basketball Association';


-- The competitions Table:
WITH competitions_data (competition_name) AS (
    VALUES
        ('Junior Domestic')
)
INSERT INTO competitions (organisation_id, competition_name, created_by_user_id)
SELECT
    o.organisation_id,
    cd.competition_name,
    u.user_account_id AS created_by_user_id
FROM competitions_data cd
JOIN organisations o ON o.organisation_name = 'Kilsyth Basketball Association'
JOIN users u ON u.email = 'samuel@whitelinegroup.com.au';


-- The seasons Table:
INSERT INTO seasons (competition_id, season_name, starting_date, ending_date, visibility, created_by_user_id)
SELECT
    c.competition_id,
    'Winter 2024',
    '2024-04-20'::DATE,
    '2024-09-21'::DATE,
    'INTERNAL',
    u.user_account_id
FROM competitions c
JOIN organisations o ON c.organisation_id = o.organisation_id
JOIN users u ON u.email = 'samuel@whitelinegroup.com.au'
WHERE c.competition_name = 'Junior Domestic'
    AND o.organisation_name = 'Kilsyth Basketball Association';


-- The season_days Table:
INSERT INTO season_days (season_id, season_day_name, season_day_label, week_day, window_start, window_end, active, created_by_user_id)
SELECT
    s.season_id,
    v.day_name AS season_day_name,
    CASE
        WHEN v.day_name = 'SATURDAY' THEN 'SATURDAY - Boys Junior Domestic'::text
        ELSE NULL::text
    END AS season_day_label,
    v.week_day,
    time '08:00:00' AS window_start,
    time '18:00:00' AS window_end,
    EXISTS (
        SELECT 1
        FROM round_dates rd
        JOIN rounds r   ON r.round_id  = rd.round_id
        JOIN dates  d   ON d.date_id   = rd.date_id
        WHERE r.season_id = s.season_id
          AND d.date_day  = v.day_name
    ) AS active,
    u.user_account_id AS created_by_user_id
FROM (
    VALUES
      ('MONDAY'   , 1),
      ('TUESDAY'  , 2),
      ('WEDNESDAY', 3),
      ('THURSDAY' , 4),
      ('FRIDAY'   , 5),
      ('SATURDAY' , 6),
      ('SUNDAY'   , 7)
) AS v(day_name, week_day)
JOIN seasons s ON s.season_name = 'Winter 2024'
JOIN competitions c ON c.competition_id = s.competition_id
JOIN organisations o ON o.organisation_id = c.organisation_id
JOIN users u ON u.email = 'samuel@whitelinegroup.com.au'
WHERE c.competition_name = 'Junior Domestic'
    AND o.organisation_name = 'Kilsyth Basketball Association';




-- VENUES SETUP
-- The venues Table:
WITH venues_data (venue_name, venue_address, display_order, indoor, accessible, total_courts) AS (
    VALUES
        ('Kilsyth Basketball Stadium', '115 Liverpool Road, Kilsyth VIC 3137', 1, TRUE, TRUE, 0),
        ('Lilydale Basketball Stadium', '26 Hutchinson Street, Lilydale VIC 3140', 2, TRUE, TRUE, 0),
        ('Melba Basketball Stadium', '20 Brentall Road, Croydon VIC 3136', 3, TRUE, TRUE, 0),
        ('Oxley Basketball Stadium', 'Old Melbourne Road, Chirnside Park VIC 3116', 4, TRUE, TRUE, 0)
)
INSERT INTO venues (organisation_id, venue_name, venue_address, display_order, indoor, accessible, total_courts, created_by_user_id)
SELECT
    o.organisation_id,
    vd.venue_name,
    vd.venue_address,
    vd.display_order,
    vd.indoor,
    vd.accessible,
    vd.total_courts,
    u.user_account_id AS created_by_user_id
FROM venues_data vd
JOIN organisations o ON o.organisation_name = 'Kilsyth Basketball Association'
JOIN users u ON u.email = 'samuel@whitelinegroup.com.au';


-- The courts Table:
WITH courts_data (venue_name, court_code, court_name, display_order, surface, indoor) AS (
    VALUES
        ('Kilsyth Basketball Stadium', 'K1', 'Court 1', 1, TRUE, TRUE),
        ('Kilsyth Basketball Stadium', 'K2', 'Court 2', 2, TRUE, TRUE),
        ('Kilsyth Basketball Stadium', 'K3', 'Court 3', 3, TRUE, TRUE),
        ('Kilsyth Basketball Stadium', 'K4', 'Court 4', 4, TRUE, TRUE),
        ('Kilsyth Basketball Stadium', 'K5', 'Court 5', 5, TRUE, TRUE),
        ('Kilsyth Basketball Stadium', 'K6', 'Court 6', 6, TRUE, TRUE),
        ('Lilydale Basketball Stadium', 'L1', 'Court 1', 1, TRUE, TRUE),
        ('Lilydale Basketball Stadium', 'L2', 'Court 2', 2, TRUE, TRUE),
        ('Lilydale Basketball Stadium', 'L3', 'Court 3', 3, TRUE, TRUE),
        ('Lilydale Basketball Stadium', 'L4', 'Court 4', 4, TRUE, TRUE),
        ('Melba Basketball Stadium', 'M1', 'Court 1', 1, TRUE, TRUE),
        ('Melba Basketball Stadium', 'M2', 'Court 2', 2, TRUE, TRUE),
        ('Melba Basketball Stadium', 'M3', 'Court 3', 3, TRUE, TRUE),
        ('Melba Basketball Stadium', 'M4', 'Court 4', 4, TRUE, TRUE),
        ('Oxley Basketball Stadium', 'OX1', 'Court 1', 1, TRUE, TRUE),
        ('Oxley Basketball Stadium', 'OX2', 'Court 2', 2, TRUE, TRUE),
        ('Oxley Basketball Stadium', 'OX3', 'Court 3', 3, TRUE, TRUE),
        ('Oxley Basketball Stadium', 'OX4', 'Court 4', 4, TRUE, TRUE),
        ('Oxley Basketball Stadium', 'OX5', 'Court 5', 5, TRUE, TRUE)
)
INSERT INTO courts (venue_id, court_code, court_name, display_order, surface, indoor, created_by_user_id)
SELECT
    v.venue_id,
    cd.court_code,
    cd.court_name,
    cd.display_order,
    cd.surface,
    cd.indoor,
    u.user_account_id AS created_by_user_id
FROM courts_data cd
JOIN venues v ON cd.venue_name = v.venue_name
JOIN users u ON u.email = 'samuel@whitelinegroup.com.au';




-- TAXONOMY SETUP
-- The ages Table:
WITH ages_data (age_code, age_name, gender, age_rank) AS (
    VALUES
        ('Miniball', 'Boys - Miniball', 'BOYS', 1),
        ('U8', 'Boys - Under 8', 'BOYS', 2),
        ('U9', 'Boys - Under 9', 'BOYS', 3),
        ('U10', 'Boys - Under 10', 'BOYS', 4),
        ('U11', 'Boys - Under 11', 'BOYS', 5),
        ('U12', 'Boys - Under 12', 'BOYS', 6),
        ('U13', 'Boys - Under 13', 'BOYS', 7),
        ('U14', 'Boys - Under 14', 'BOYS', 8),
        ('U15', 'Boys - Under 15', 'BOYS', 9),
        ('U16', 'Boys - Under 16', 'BOYS', 10),
        ('U18', 'Boys - Under 18', 'BOYS', 11),
        ('U23', 'Boys - Under 23', 'BOYS', 12)
)
INSERT INTO ages (season_day_id, age_code, age_name, gender, age_rank, created_by_user_id)
SELECT
    sd.season_day_id,
    ad.age_code,
    ad.age_name,
    ad.gender,
    ad.age_rank,
    u.user_account_id AS created_by_user_id
FROM ages_data ad
JOIN seasons s ON s.season_name = 'Winter 2024'
JOIN season_days sd ON sd.season_id = s.season_id
JOIN competitions c ON c.competition_id = s.competition_id
JOIN organisations o ON o.organisation_id = c.organisation_id
JOIN users u ON u.email = 'samuel@whitelinegroup.com.au'
WHERE sd.season_day_name = 'SATURDAY'
    AND c.competition_name = 'Junior Domestic'
    AND o.organisation_name = 'Kilsyth Basketball Association';


-- The grades Table:
WITH grades_data (age_code, grade_code, grade_name, grade_rank) AS (
    VALUES
        ('Miniball', '1', '1', 1),
        ('Miniball', '2', '2', 3),
        ('Miniball', '3', '3', 4),
        ('Miniball', '4', '4', 7),

        ('U8', 'A/ARES', 'A/A RESERVE', 1),
        ('U8', 'B/BRES', 'B/B RESERVE', 3),
        ('U8', 'C', 'C GRADE', 5),
        ('U8', 'CRES', 'C RESERVE', 6),

        ('U9', 'A/ARES', 'A/A RESERVE', 1),
        ('U9', 'B', 'B GRADE', 3),
        ('U9', 'BRES', 'B RESERVE', 4),
        ('U9', 'C', 'C GRADE', 5),
        ('U9', 'CRES', 'C RESERVE', 6),

        ('U10', 'A', 'A GRADE', 1),
        ('U10', 'ARES', 'A RESERVE', 2),
        ('U10', 'B', 'B GRADE', 3),
        ('U10', 'BRES', 'B RESERVE', 4),
        ('U10', 'C', 'C GRADE', 5),
        ('U10', 'CRES', 'C RESERVE', 6),

        ('U11', 'A', 'A GRADE', 1),
        ('U11', 'ARES', 'A RESERVE', 2),
        ('U11', 'B', 'B GRADE', 3),
        ('U11', 'BRES', 'B RESERVE', 4),
        ('U11', 'C', 'C GRADE', 5),
        ('U11', 'CRES', 'C RESERVE', 6),

        ('U12', 'A/ARES', 'A/A RESERVE', 1),
        ('U12', 'B', 'B GRADE', 3),
        ('U12', 'BRES', 'B RESERVE', 4),
        ('U12', 'C', 'C GRADE', 5),
        ('U12', 'CRES', 'C RESERVE', 6),

        ('U13', 'A', 'A GRADE', 1),
        ('U13', 'ARES', 'A RESERVE', 2),
        ('U13', 'B', 'B GRADE', 3),
        ('U13', 'BRES', 'B RESERVE', 4),
        ('U13', 'C', 'C GRADE', 5),
        ('U13', 'CRES', 'C RESERVE', 6),
        ('U13', 'D', 'D GRADE', 7),

        ('U14', 'A', 'A GRADE', 1),
        ('U14', 'ARES', 'A RESERVE', 2),
        ('U14', 'B', 'B GRADE', 3),
        ('U14', 'BRES', 'B RESERVE', 4),
        ('U14', 'C', 'C GRADE', 5),
        ('U14', 'CRES', 'C RESERVE', 6),

        ('U15', 'A/ARES', 'A/A RESERVE', 1),
        ('U15', 'B', 'B GRADE', 3),
        ('U15', 'BRES', 'B RESERVE', 4),
        ('U15', 'C', 'C GRADE', 5),
        ('U15', 'CRES', 'C RESERVE', 6),

        ('U16', 'A', 'A GRADE', 1),
        ('U16', 'ARES', 'A RESERVE', 2),
        ('U16', 'B/BRES', 'B/B RESERVE', 3),
        ('U16', 'C', 'C GRADE', 5),

        ('U18', 'A', 'A GRADE', 1),
        ('U18', 'ARES', 'A RESERVE', 2),
        ('U18', 'B', 'B GRADE', 3),
        ('U18', 'BRES', 'B RESERVE', 4),
        ('U18', 'C', 'C GRADE', 5),
        ('U18', 'CRES', 'C RESERVE', 6),

        ('U23', 'A', 'A GRADE', 1),
        ('U23', 'B', 'B GRADE', 3)
)
INSERT INTO grades (age_id, grade_code, grade_name, grade_rank, created_by_user_id)
SELECT
    a.age_id,
    gd.grade_code,
    gd.grade_name,
    gd.grade_rank,
    u.user_account_id AS created_by_user_id
FROM grades_data gd
JOIN ages a ON a.age_code = gd.age_code
JOIN season_days sd ON sd.season_day_id = a.season_day_id
JOIN seasons s ON s.season_id = sd.season_id
JOIN competitions c ON c.competition_id = s.competition_id
JOIN organisations o ON o.organisation_id = c.organisation_id
JOIN users u ON u.email = 'samuel@whitelinegroup.com.au'
WHERE sd.season_day_name = 'SATURDAY'
    AND s.season_name = 'Winter 2024'
    AND c.competition_name = 'Junior Domestic'
    AND o.organisation_name = 'Kilsyth Basketball Association';


-- The teams Table:
WITH teams_data (team_code, grade_code, age_code) AS (
    VALUES
    -- Miniball
        ('MLBC B58', '1', 'Miniball'),
        ('MMB113', '1', 'Miniball'),
        ('MMB114', '1', 'Miniball'),
        ('Vikings B91', '1', 'Miniball'),
        ('KILSYTH HEAT B20', '1', 'Miniball'),
        ('Meteors B38', '1', 'Miniball'),
        ('EEBC B42', '1', 'Miniball'),
        ('SCYC B35', '2', 'Miniball'),
        ('Meteors B39', '2', 'Miniball'),
        ('SEBC Saints B69', '2', 'Miniball'),
        ('Wandin Warriors B5', '2', 'Miniball'),
        ('EEBC B41', '2', 'Miniball'),
        ('MLBC B59', '2', 'Miniball'),
        ('Crossover United B1', '2', 'Miniball'),
        ('Vikings B92', '2', 'Miniball'),
        ('Crossover United B2', '2', 'Miniball'),
        ('KILSYTH HEAT B19', '3', 'Miniball'),
        ('MLBC B61', '3', 'Miniball'),
        ('Meteors B40', '3', 'Miniball'),
        ('MMB115', '3', 'Miniball'),
        ('SEBC Saints B68', '3', 'Miniball'),
        ('Wandin Warriors B6', '3', 'Miniball'),
        ('MMB118', '3', 'Miniball'),
        ('Venom B1', '3', 'Miniball'),
        ('EEBC B43', '3', 'Miniball'),
        ('MLBC B60', '4', 'Miniball'),
        ('MMB116', '4', 'Miniball'),
        ('Meteors B41', '4', 'Miniball'),
        ('SEBC Saints B74', '4', 'Miniball'),
        ('MMB117', '4', 'Miniball'),
        ('MMB119', '4', 'Miniball'),
    -- U8
        ('SCYC B33', 'A/ARES', 'U8'),
        ('SEBC Saints B66', 'A/ARES', 'U8'),
        ('EEBC B39', 'A/ARES', 'U8'),
        ('SEBC Saints B64', 'A/ARES', 'U8'),
        ('Meteors B35', 'A/ARES', 'U8'),
        ('MMB104', 'A/ARES', 'U8'),
        ('MLBC B53', 'A/ARES', 'U8'),
        ('MMB103', 'A/ARES', 'U8'),
        ('MMB102', 'A/ARES', 'U8'),
        ('Vikings B81', 'B/BRES', 'U8'),
        ('Wandin Warriors B3', 'B/BRES', 'U8'),
        ('MMB107', 'B/BRES', 'U8'),
        ('Meteors B36', 'B/BRES', 'U8'),
        ('Crossover United B3', 'B/BRES', 'U8'),
        ('MLBC B54', 'B/BRES', 'U8'),
        ('Crossover United B4', 'B/BRES', 'U8'),
        ('KILSYTH HEAT B18', 'B/BRES', 'U8'),
        ('MMB105', 'B/BRES', 'U8'),
        ('EEBC B40', 'C', 'U8'),
        ('MMB106', 'C', 'U8'),
        ('MLBC B56', 'C', 'U8'),
        ('Vikings B83', 'C', 'U8'),
        ('MLBC B55', 'C', 'U8'),
        ('SEBC Saints B70', 'C', 'U8'),
        ('Fosters Phantoms B19', 'C', 'U8'),
        ('SEBC Saints B65', 'C', 'U8'),
        ('MMB109', 'C', 'U8'),
        ('Meteors B37', 'C', 'U8'),
        ('MMB112', 'CRES', 'U8'),
        ('MMB108', 'CRES', 'U8'),
        ('Fosters Phantoms B20', 'CRES', 'U8'),
        ('Vikings B82', 'CRES', 'U8'),
        ('SCYC B34', 'CRES', 'U8'),
        ('MMB110', 'CRES', 'U8'),
        ('MLBC B57', 'CRES', 'U8'),
        ('SEBC Saints B67', 'CRES', 'U8'),
        ('MMB111', 'CRES', 'U8'),
    -- U9
        ('MMB92', 'A/ARES', 'U9'),
        ('MLBC B48', 'A/ARES', 'U9'),
        ('SEBC Saints B60', 'A/ARES', 'U9'),
        ('KILSYTH HEAT B15', 'A/ARES', 'U9'),
        ('Vikings B72', 'A/ARES', 'U9'),
        ('EEBC B33', 'A/ARES', 'U9'),
        ('Vikings B71', 'A/ARES', 'U9'),
        ('Crossover United B7', 'A/ARES', 'U9'),
        ('MMB91', 'A/ARES', 'U9'),
        ('MMB94', 'B', 'U9'),
        ('Vikings B73', 'B', 'U9'),
        ('EEBC B34', 'B', 'U9'),
        ('SEBC Saints B61', 'B', 'U9'),
        ('Meteors B32', 'B', 'U9'),
        ('Fosters Phantoms B18', 'B', 'U9'),
        ('Crossover United B6', 'B', 'U9'),
        ('SCYC B32', 'B', 'U9'),
        ('MMB93', 'B', 'U9'),
        ('MMB95', 'BRES', 'U9'),
        ('Venom B3', 'BRES', 'U9'),
        ('Meteors B33', 'BRES', 'U9'),
        ('SEBC Saints B63', 'BRES', 'U9'),
        ('Crossover United B5', 'BRES', 'U9'),
        ('MMB96', 'BRES', 'U9'),
        ('EEBC B35', 'BRES', 'U9'),
        ('MLBC B49', 'BRES', 'U9'),
        ('EEBC B36', 'BRES', 'U9'),
        ('KILSYTH HEAT B16', 'C', 'U9'),
        ('Vikings B74', 'C', 'U9'),
        ('Meteors B34', 'C', 'U9'),
        ('SEBC Saints B72', 'C', 'U9'),
        ('KILSYTH HEAT B17', 'C', 'U9'),
        ('MMB99', 'C', 'U9'),
        ('MLBC B50', 'C', 'U9'),
        ('Wandin Warriors B2', 'C', 'U9'),
        ('SEBC Saints B62', 'C', 'U9'),
        ('MMB101', 'CRES', 'U9'),
        ('MLBC B51', 'CRES', 'U9'),
        ('MMB97', 'CRES', 'U9'),
        ('Flashes B13', 'CRES', 'U9'),
        ('MMB98', 'CRES', 'U9'),
        ('EEBC B37', 'CRES', 'U9'),
        ('EEBC B38', 'CRES', 'U9'),
        ('MLBC B52', 'CRES', 'U9'),
        ('MMB100', 'CRES', 'U9'),
    -- U10
        ('MLBC B42', 'A', 'U10'),
        ('Meteors B26', 'A', 'U10'),
        ('Vikings B61', 'A', 'U10'),
        ('SEBC Saints B53', 'A', 'U10'),
        ('EEBC B28', 'A', 'U10'),
        ('Crossover United B10', 'A', 'U10'),
        ('SEBC Saints B54', 'A', 'U10'),
        ('MMB80', 'A', 'U10'),
        ('MMB81', 'ARES', 'U10'),
        ('EEBC B29', 'ARES', 'U10'),
        ('KILSYTH HEAT B13', 'ARES', 'U10'),
        ('SEBC Saints B55', 'ARES', 'U10'),
        ('Meteors B27', 'ARES', 'U10'),
        ('MMB83', 'ARES', 'U10'),
        ('MMB82', 'ARES', 'U10'),
        ('MLBC B43', 'ARES', 'U10'),
        ('EEBC B30', 'B', 'U10'),
        ('SCYC B30', 'B', 'U10'),
        ('SEBC Saints B56', 'B', 'U10'),
        ('Vikings B62', 'B', 'U10'),
        ('MLBC B44', 'B', 'U10'),
        ('MMB84', 'B', 'U10'),
        ('MLBC B45', 'B', 'U10'),
        ('Wandin Warriors B1', 'B', 'U10'),
        ('Crossover United B8', 'B', 'U10'),
        ('SEBC Saints B57', 'BRES', 'U10'),
        ('MLBC B46', 'BRES', 'U10'),
        ('Flashes B12', 'BRES', 'U10'),
        ('MMB86', 'BRES', 'U10'),
        ('Meteors B28', 'BRES', 'U10'),
        ('SEBC Saints B58', 'BRES', 'U10'),
        ('Meteors B29', 'BRES', 'U10'),
        ('MMB85', 'BRES', 'U10'),
        ('Venom B4', 'BRES', 'U10'),
        ('Fosters Phantoms B17', 'C', 'U10'),
        ('Vikings B64', 'C', 'U10'),
        ('Meteors B30', 'C', 'U10'),
        ('MMB89', 'C', 'U10'),
        ('Crossover United B9', 'C', 'U10'),
        ('EEBC B31', 'C', 'U10'),
        ('SCYC B31', 'C', 'U10'),
        ('SEBC Saints B59', 'C', 'U10'),
        ('Fosters Phantoms B16', 'C', 'U10'),
        ('MMB88', 'CRES', 'U10'),
        ('EEBC B32', 'CRES', 'U10'),
        ('MMB90', 'CRES', 'U10'),
        ('Meteors B31', 'CRES', 'U10'),
        ('KILSYTH HEAT B14', 'CRES', 'U10'),
        ('MLBC B47', 'CRES', 'U10'),
        ('MMB120', 'CRES', 'U10'),
        ('Vikings B63', 'CRES', 'U10'),
        ('MMB87', 'CRES', 'U10'),
    -- U11
        ('SEBC Saints B47', 'A', 'U11'),
        ('Crossover United B11', 'A', 'U11'),
        ('SEBC Saints B49', 'A', 'U11'),
        ('EEBC B23', 'A', 'U11'),
        ('SCYC B27', 'A', 'U11'),
        ('Crossover United B12', 'A', 'U11'),
        ('SEBC Saints B48', 'A', 'U11'),
        ('MMB68', 'A', 'U11'),
        ('SEBC Saints B50', 'ARES', 'U11'),
        ('Vikings B51', 'ARES', 'U11'),
        ('Crossover United B15', 'ARES', 'U11'),
        ('Venom B5', 'ARES', 'U11'),
        ('MMB70', 'ARES', 'U11'),
        ('MMB71', 'ARES', 'U11'),
        ('EEBC B24', 'ARES', 'U11'),
        ('MMB69', 'ARES', 'U11'),
        ('Vikings B52', 'B', 'U11'),
        ('Meteors B24', 'B', 'U11'),
        ('EEBC B25', 'B', 'U11'),
        ('Crossover United B13', 'B', 'U11'),
        ('MLBC B37', 'B', 'U11'),
        ('MMB74', 'B', 'U11'),
        ('SEBC Saints B51', 'B', 'U11'),
        ('MMB73', 'B', 'U11'),
        ('KILSYTH HEAT B11', 'B', 'U11'),
        ('MMB75', 'BRES', 'U11'),
        ('Vikings B54', 'BRES', 'U11'),
        ('MLBC B40', 'BRES', 'U11'),
        ('SCYC B28', 'BRES', 'U11'),
        ('MLBC B38', 'BRES', 'U11'),
        ('SEBC Saints B52', 'BRES', 'U11'),
        ('MMB77', 'BRES', 'U11'),
        ('MMB76', 'BRES', 'U11'),
        ('MMB72', 'BRES', 'U11'),
        ('MMB78', 'C', 'U11'),
        ('KILSYTH HEAT B12', 'C', 'U11'),
        ('Crossover United B14', 'C', 'U11'),
        ('Flashes B11', 'C', 'U11'),
        ('Vikings B53', 'C', 'U11'),
        ('MLBC B39', 'C', 'U11'),
        ('EEBC B26', 'C', 'U11'),
        ('SCYC B29', 'CRES', 'U11'),
        ('MMB79', 'CRES', 'U11'),
        ('MLBC B41', 'CRES', 'U11'),
        ('Meteors B25', 'CRES', 'U11'),
        ('EEBC B27', 'CRES', 'U11'),
    -- U12
        ('EEBC B19', 'A/ARES', 'U12'),
        ('MMB56', 'A/ARES', 'U12'),
        ('Crossover United B19', 'A/ARES', 'U12'),
        ('Meteors B20', 'A/ARES', 'U12'),
        ('SEBC Saints B40', 'A/ARES', 'U12'),
        ('MMB57', 'A/ARES', 'U12'),
        ('MLBC B33', 'A/ARES', 'U12'),
        ('SEBC Saints B42', 'A/ARES', 'U12'),
        ('Fosters Phantoms B14', 'A/ARES', 'U12'),
        ('SCYC B23', 'A/ARES', 'U12'),
        ('MLBC B35', 'B', 'U12'),
        ('EEBC B20', 'B', 'U12'),
        ('SEBC Saints B41', 'B', 'U12'),
        ('MMB59', 'B', 'U12'),
        ('Crossover United B18', 'B', 'U12'),
        ('MMB58', 'B', 'U12'),
        ('MLBC B34', 'B', 'U12'),
        ('MMB61', 'BRES', 'U12'),
        ('Meteors B21', 'BRES', 'U12'),
        ('Vikings B41', 'BRES', 'U12'),
        ('SEBC Saints B44', 'BRES', 'U12'),
        ('KILSYTH HEAT B08', 'BRES', 'U12'),
        ('Meteors B22', 'BRES', 'U12'),
        ('Crossover United B16', 'BRES', 'U12'),
        ('MMB60', 'BRES', 'U12'),
        ('SEBC Saints B43', 'BRES', 'U12'),
        ('KILSYTH HEAT B09', 'BRES', 'U12'),
        ('SCYC B24', 'BRES', 'U12'),
        ('MMB64', 'C', 'U12'),
        ('Flashes B10', 'C', 'U12'),
        ('KILSYTH HEAT B10', 'C', 'U12'),
        ('SEBC Saints B46', 'C', 'U12'),
        ('EEBC B22', 'C', 'U12'),
        ('SEBC Saints B45', 'C', 'U12'),
        ('EEBC B21', 'C', 'U12'),
        ('Venom B6', 'C', 'U12'),
        ('MMB62', 'C', 'U12'),
        ('Crossover United B17', 'C', 'U12'),
        ('MMB67', 'CRES', 'U12'),
        ('SCYC B26', 'CRES', 'U12'),
        ('MMB65', 'CRES', 'U12'),
        ('Vikings B42', 'CRES', 'U12'),
        ('MMB63', 'CRES', 'U12'),
        ('MLBC B36', 'CRES', 'U12'),
        ('Meteors B23', 'CRES', 'U12'),
        ('Fosters Phantoms B15', 'CRES', 'U12'),
        ('MMB66', 'CRES', 'U12'),
    -- U13
        ('MMB45', 'A', 'U13'),
        ('SCYC B17', 'A', 'U13'),
        ('SEBC Saints B31', 'A', 'U13'),
        ('Vikings B31', 'A', 'U13'),
        ('SEBC Saints B30', 'A', 'U13'),
        ('Crossover United B22', 'A', 'U13'),
        ('SEBC Saints B29', 'A', 'U13'),
        ('EEBC B15', 'A', 'U13'),
        ('MMB44', 'A', 'U13'),
        ('SEBC Saints B32', 'A', 'U13'),
        ('Crossover United B23', 'ARES', 'U13'),
        ('EEBC B16', 'ARES', 'U13'),
        ('Vikings B32', 'ARES', 'U13'),
        ('MMB46', 'ARES', 'U13'),
        ('MMB47', 'ARES', 'U13'),
        ('SCYC B18', 'ARES', 'U13'),
        ('Meteors B16', 'ARES', 'U13'),
        ('MLBC B26', 'ARES', 'U13'),
        ('MMB48', 'B', 'U13'),
        ('SEBC Saints B35', 'B', 'U13'),
        ('SEBC Saints B33', 'B', 'U13'),
        ('SEBC Saints B34', 'B', 'U13'),
        ('Crossover United B21', 'B', 'U13'),
        ('MLBC B27', 'B', 'U13'),
        ('Meteors B17', 'B', 'U13'),
        ('MMB50', 'B', 'U13'),
        ('MMB49', 'B', 'U13'),
        ('SCYC B19', 'B', 'U13'),
        ('EEBC B17', 'B', 'U13'),
        ('SEBC Saints B36', 'BRES', 'U13'),
        ('Venom B10', 'BRES', 'U13'),
        ('MMB51', 'BRES', 'U13'),
        ('SEBC Saints B38', 'BRES', 'U13'),
        ('SCYC B20', 'BRES', 'U13'),
        ('MLBC B28', 'BRES', 'U13'),
        ('EEBC B18', 'BRES', 'U13'),
        ('Vikings B33', 'BRES', 'U13'),
        ('MMB52', 'C', 'U13'),
        ('MLBC B29', 'C', 'U13'),
        ('VIKINGS B34', 'C', 'U13'),
        ('SCYC B21', 'C', 'U13'),
        ('Flashes B9', 'C', 'U13'),
        ('MLBC B30', 'C', 'U13'),
        ('SEBC Saints B37', 'C', 'U13'),
        ('Meteors B19', 'C', 'U13'),
        ('KILSYTH HEAT B07', 'C', 'U13'),
        ('Crossover United B20', 'C', 'U13'),
        ('MLBC B31', 'CRES', 'U13'),
        ('SCYC B25', 'CRES', 'U13'),
        ('MMB53', 'CRES', 'U13'),
        ('MMB54', 'CRES', 'U13'),
        ('Wandin Warriors B4', 'CRES', 'U13'),
        ('Meteors B18', 'CRES', 'U13'),
        ('SCYC B22', 'CRES', 'U13'),
        ('Venom B7', 'D', 'U13'),
        ('EEBC B67', 'D', 'U13'),
        ('MMB55', 'D', 'U13'),
        ('MLBC B32', 'D', 'U13'),
        ('SEBC Saints B39', 'D', 'U13'),
    -- U14
        ('Crossover United B27', 'A', 'U14'),
        ('SEBC Saints B21', 'A', 'U14'),
        ('SEBC Saints B23', 'A', 'U14'),
        ('MMB33', 'A', 'U14'),
        ('MLBC B19', 'A', 'U14'),
        ('MMB32', 'A', 'U14'),
        ('MLBC B20', 'A', 'U14'),
        ('EEBC B11', 'A', 'U14'),
        ('MMB34', 'A', 'U14'),
        ('Vikings B21', 'A', 'U14'),
        ('SEBC Saints B22', 'A', 'U14'),
        ('SEBC Saints B24', 'ARES', 'U14'),
        ('MMB35', 'ARES', 'U14'),
        ('KILSYTH HEAT B05', 'ARES', 'U14'),
        ('Meteors B14', 'ARES', 'U14'),
        ('Crossover United B25', 'ARES', 'U14'),
        ('Healesville Hornets', 'ARES', 'U14'),
        ('MMB37', 'ARES', 'U14'),
        ('MLBC B21', 'B', 'U14'),
        ('MLBC B22', 'B', 'U14'),
        ('MMB39', 'B', 'U14'),
        ('MMB38', 'B', 'U14'),
        ('MMB36', 'B', 'U14'),
        ('Flashes B8', 'B', 'U14'),
        ('MLBC B23', 'B', 'U14'),
        ('SEBC Saints B26', 'B', 'U14'),
        ('EEBC B12', 'B', 'U14'),
        ('SCYC B16', 'BRES', 'U14'),
        ('EEBC B13', 'BRES', 'U14'),
        ('KILSYTH HEAT B06', 'BRES', 'U14'),
        ('MMB40', 'BRES', 'U14'),
        ('Fosters Phantoms B12', 'BRES', 'U14'),
        ('SEBC Saints B25', 'BRES', 'U14'),
        ('Venom B9', 'BRES', 'U14'),
        ('Crossover United B29', 'BRES', 'U14'),
        ('Vikings B22', 'BRES', 'U14'),
        ('Meteors B15', 'BRES', 'U14'),
        ('Flashes B7', 'C', 'U14'),
        ('SCYC B14', 'C', 'U14'),
        ('Crossover United B26', 'C', 'U14'),
        ('MMB43', 'C', 'U14'),
        ('EEBC B14', 'C', 'U14'),
        ('SCYC B15', 'C', 'U14'),
        ('SEBC Saints B27', 'C', 'U14'),
        ('Fosters Phantoms B13', 'C', 'U14'),
        ('MMB42', 'CRES', 'U14'),
        ('MMB41', 'CRES', 'U14'),
        ('Crossover United B24', 'CRES', 'U14'),
        ('MLBC B25', 'CRES', 'U14'),
        ('MLBC B24', 'CRES', 'U14'),
        ('SEBC Saints B28', 'CRES', 'U14'),
    -- U15
        ('MLBC B14', 'A/ARES', 'U15'),
        ('SEBC Saints B14', 'A/ARES', 'U15'),
        ('MLBC B15', 'A/ARES', 'U15'),
        ('MMB21', 'A/ARES', 'U15'),
        ('SCYC B10', 'A/ARES', 'U15'),
        ('MLBC B13', 'A/ARES', 'U15'),
        ('SEBC Saints B15', 'A/ARES', 'U15'),
        ('EEBC B09', 'A/ARES', 'U15'),
        ('MMB24', 'A/ARES', 'U15'),
        ('Vikings B11', 'A/ARES', 'U15'),
        ('Meteors B10', 'A/ARES', 'U15'),
        ('MMB23', 'B', 'U15'),
        ('SEBC Saints B16', 'B', 'U15'),
        ('Crossover United B28', 'B', 'U15'),
        ('MLBC B16', 'B', 'U15'),
        ('MMB22', 'B', 'U15'),
        ('SEBC Saints B17', 'B', 'U15'),
        ('MMB26', 'B', 'U15'),
        ('Fosters Phantoms B10', 'B', 'U15'),
        ('EEBC B10', 'BRES', 'U15'),
        ('MLBC B17', 'BRES', 'U15'),
        ('SEBC Saints B18', 'BRES', 'U15'),
        ('MMB28', 'BRES', 'U15'),
        ('MMB25', 'BRES', 'U15'),
        ('MMB29', 'BRES', 'U15'),
        ('Meteors B11', 'BRES', 'U15'),
        ('Vikings B12', 'BRES', 'U15'),
        ('KILSYTH HEAT B03', 'BRES', 'U15'),
        ('Meteors B12', 'BRES', 'U15'),
        ('MLBC B18', 'C', 'U15'),
        ('MMB31', 'C', 'U15'),
        ('SCYC B11', 'C', 'U15'),
        ('MMB27', 'C', 'U15'),
        ('MMB30', 'C', 'U15'),
        ('Crossover United B30', 'C', 'U15'),
        ('SEBC Saints B19', 'C', 'U15'),
        ('SCYC B13', 'C', 'U15'),
        ('Fosters Phantoms B11', 'C', 'U15'),
        ('SCYC B12', 'CRES', 'U15'),
        ('Flashes B6', 'CRES', 'U15'),
        ('Meteors B13', 'CRES', 'U15'),
        ('SEBC Saints B20', 'CRES', 'U15'),
        ('Vikings B13', 'CRES', 'U15'),
    -- U16
        ('MLBC B09', 'A', 'U16'),
        ('MMB14', 'A', 'U16'),
        ('SEBC Saints B09', 'A', 'U16'),
        ('EEBC B07', 'A', 'U16'),
        ('Crossover United B32', 'A', 'U16'),
        ('EEBC B06', 'A', 'U16'),
        ('MMB15', 'A', 'U16'),
        ('MLBC B10', 'ARES', 'U16'),
        ('MMB16', 'ARES', 'U16'),
        ('Vikings B05', 'ARES', 'U16'),
        ('SCYC B07', 'ARES', 'U16'),
        ('Meteors B07', 'ARES', 'U16'),
        ('SCYC B06', 'ARES', 'U16'),
        ('SEBC Saints B10', 'ARES', 'U16'),
        ('Fosters Phantoms B07', 'ARES', 'U16'),
        ('EEBC B08', 'B/BRES', 'U16'),
        ('MMB20', 'B/BRES', 'U16'),
        ('Meteors B08', 'B/BRES', 'U16'),
        ('Fosters Phantoms B08', 'B/BRES', 'U16'),
        ('MMB17', 'B/BRES', 'U16'),
        ('MMB19', 'B/BRES', 'U16'),
        ('Crossover United B31', 'B/BRES', 'U16'),
        ('MLBC B11', 'B/BRES', 'U16'),
        ('SCYC B08', 'B/BRES', 'U16'),
        ('Flashes B5', 'B/BRES', 'U16'),
        ('SCYC B09', 'C', 'U16'),
        ('MMB18', 'C', 'U16'),
        ('SEBC Saints B12', 'C', 'U16'),
        ('SEBC Saints B13', 'C', 'U16'),
        ('Meteors B09', 'C', 'U16'),
        ('MLBC B12', 'C', 'U16'),
        ('SEBC Saints B11', 'C', 'U16'),
        ('Crossover United B33', 'C', 'U16'),
        ('Fosters Phantoms B09', 'C', 'U16'),
    -- U18
        ('SEBC Saints B03', 'A', 'U18'),
        ('SCYC B04', 'A', 'U18'),
        ('SEBC Saints B04', 'A', 'U18'),
        ('MLBC B03', 'A', 'U18'),
        ('Meteors B02', 'A', 'U18'),
        ('SEBC Saints B05', 'A', 'U18'),
        ('MMB04', 'A', 'U18'),
        ('EEBC B02', 'A', 'U18'),
        ('Fosters Phantoms B03', 'A', 'U18'),
        ('MMB06', 'ARES', 'U18'),
        ('MMB05', 'ARES', 'U18'),
        ('Crossover United B34', 'ARES', 'U18'),
        ('Vikings B02', 'ARES', 'U18'),
        ('Fosters Phantoms B04', 'ARES', 'U18'),
        ('Meteors B03', 'ARES', 'U18'),
        ('EEBC B03', 'ARES', 'U18'),
        ('Vikings B01', 'B', 'U18'),
        ('MMB07', 'B', 'U18'),
        ('SCYC B05', 'B', 'U18'),
        ('SEBC Saints B06', 'B', 'U18'),
        ('Crossover United B36', 'B', 'U18'),
        ('MMB08', 'B', 'U18'),
        ('MLBC B04', 'B', 'U18'),
        ('Fosters Phantoms B05', 'B', 'U18'),
        ('Vikings B03', 'BRES', 'U18'),
        ('Meteors B04', 'BRES', 'U18'),
        ('EEBC B04', 'BRES', 'U18'),
        ('Flashes B3', 'BRES', 'U18'),
        ('Fosters Phantoms B06', 'BRES', 'U18'),
        ('SEBC Saints B07', 'BRES', 'U18'),
        ('Meteors B06', 'C', 'U18'),
        ('SEBC Saints B08', 'C', 'U18'),
        ('MMB12', 'C', 'U18'),
        ('MMB10', 'C', 'U18'),
        ('Crossover United B35', 'C', 'U18'),
        ('EEBC B05', 'C', 'U18'),
        ('MLBC B06', 'C', 'U18'),
        ('MLBC B08', 'CRES', 'U18'),
        ('MLBC B07', 'CRES', 'U18'),
        ('MLBC B05', 'CRES', 'U18'),
        ('Meteors B05', 'CRES', 'U18'),
        ('MMB13', 'CRES', 'U18'),
        ('KILSYTH HEAT B01', 'CRES', 'U18'),
    -- U23
        ('SCYC B02', 'A', 'U23'),
        ('SEBC Saints B01', 'A', 'U23'),
        ('Fosters Phantoms B02', 'A', 'U23'),
        ('MMB01', 'A', 'U23'),
        ('SCYC B01', 'A', 'U23'),
        ('SEBC Saints B73', 'B', 'U23'),
        ('SCYC B03', 'B', 'U23'),
        ('MLBC B01', 'B', 'U23'),
        ('SEBC Saints B02', 'B', 'U23'),
        ('MMB03', 'B', 'U23'),
        ('EEBC B01', 'B', 'U23'),
        ('MMB02', 'B', 'U23'),
        ('Meteors B01', 'B', 'U23'),
        ('MLBC B02', 'B', 'U23'),
        ('Fosters Phantoms B01', 'B', 'U23'),
        ('MMB11', 'B', 'U23'),
        ('SEBC Saints B71', 'B', 'U23')
)
INSERT INTO teams (grade_id, team_code, created_by_user_id)
SELECT
    g.grade_id,
    td.team_code,
    u.user_account_id AS created_by_user_id
FROM teams_data td
JOIN ages a ON a.age_code = td.age_code
JOIN season_days sd ON sd.season_day_id = a.season_day_id
JOIN seasons s ON s.season_id = sd.season_id
JOIN competitions c ON c.competition_id = s.competition_id
JOIN organisations o ON o.organisation_id = c.organisation_id
JOIN grades g ON g.age_id = a.age_id AND g.grade_code = td.grade_code
JOIN users u ON u.email = 'samuel@whitelinegroup.com.au'
WHERE sd.season_day_name = 'SATURDAY'
    AND s.season_name = 'Winter 2024'
    AND c.competition_name = 'Junior Domestic'
    AND o.organisation_name = 'Kilsyth Basketball Association';





-- TIMEPLAN SETUP
-- The rounds Table:
WITH rounds_data (round_number, round_label, round_type) AS (
    VALUES
        (1, 'R1', 'GRADING'),
        (2, 'R2', 'GRADING'),
        (3, 'R3', 'GRADING'),
        (4, 'R4', 'GRADING'),
        (5, 'R5', 'GRADING'),
        (6, 'R6', 'REGULAR'),
        (7, 'R7', 'REGULAR'),
        (8, 'R8', 'REGULAR'),
        (9, 'R9', 'REGULAR'),
        (10, 'R10', 'REGULAR'),
        (11, 'R11', 'REGULAR'),
        (12, 'R12', 'REGULAR'),
        (13, 'R13', 'REGULAR'),
        (14, 'R14', 'REGULAR'),
        (15, 'R15', 'REGULAR'),
        (16, 'R16', 'REGULAR'),
        (17, 'R17', 'REGULAR'),
        (18, 'R18', 'REGULAR'),
        (19, 'FR1', 'FINALS'),
        (20, 'PF', 'FINALS'),
        (21, 'GF', 'FINALS')
)
INSERT INTO rounds (season_id, round_number, round_label, round_type, created_by_user_id)
SELECT
    s.season_id,
    rd.round_number,
    rd.round_label,
    rd.round_type,
    u.user_account_id AS created_by_user_id
FROM rounds_data rd
JOIN seasons s ON s.season_name = 'Winter 2024'
JOIN competitions c ON s.competition_id = c.competition_id
JOIN organisations o ON c.organisation_id = o.organisation_id
JOIN users u ON u.email = 'samuel@whitelinegroup.com.au'
WHERE c.competition_name = 'Junior Domestic'
    AND o.organisation_name = 'Kilsyth Basketball Association';


-- The round_settings Table:
WITH round_settings_data (round_settings_number) AS (
    VALUES
        (1)
)
INSERT INTO round_settings (season_day_id, round_settings_number, created_by_user_id)
SELECT
    sd.season_day_id,
    rsd.round_settings_number,
    u.user_account_id AS created_by_user_id
FROM round_settings_data rsd
JOIN season_days sd ON sd.season_day_name = 'SATURDAY'
JOIN seasons s ON s.season_id = sd.season_id
JOIN competitions c ON c.competition_id = s.competition_id
JOIN organisations o ON o.organisation_id = c.organisation_id
JOIN users u ON u.email = 'samuel@whitelinegroup.com.au'
WHERE s.season_name = 'Winter 2024'
    AND c.competition_name = 'Junior Domestic'
    AND o.organisation_name = 'Kilsyth Basketball Association';


-- The time_slots Table:
WITH time_slots_data (start_time_value, end_time_value, buffer_value) AS (
    VALUES
        ('08:00:00'::TIME, '08:50:00'::TIME, 10),
        ('08:50:00'::TIME, '09:40:00'::TIME, 10),
        ('09:40:00'::TIME, '10:30:00'::TIME, 10),
        ('10:30:00'::TIME, '11:20:00'::TIME, 10),
        ('11:20:00'::TIME, '12:10:00'::TIME, 10),
        ('12:10:00'::TIME, '13:00:00'::TIME, 10),
        ('13:00:00'::TIME, '13:50:00'::TIME, 10),
        ('13:50:00'::TIME, '14:40:00'::TIME, 10),
        ('14:40:00'::TIME, '15:30:00'::TIME, 10),
        ('15:30:00'::TIME, '16:20:00'::TIME, 10),
        ('16:20:00'::TIME, '17:10:00'::TIME, 10),
        ('17:10:00'::TIME, '18:00:00'::TIME, 10),
        ('18:00:00'::TIME, '18:50:00'::TIME, 10)
)
INSERT INTO time_slots (season_day_id, start_time_id, end_time_id, start_time, end_time, buffer_minutes, duration_minutes, created_by_user_id)
SELECT
    sd.season_day_id,
    dts.time_id AS start_time_id,
    dte.time_id AS end_time_id,
    tsd.start_time_value AS start_time,
    tsd.end_time_value AS end_time,
    tsd.buffer_value AS buffer_minutes,
    (EXTRACT(EPOCH FROM (tsd.end_time_value - tsd.start_time_value)) / 60)::int - tsd.buffer_value AS duration_minutes,
    u.user_account_id AS created_by_user_id
FROM time_slots_data tsd
JOIN default_times dts ON dts.time_value = tsd.start_time_value
JOIN default_times dte ON dte.time_value   = tsd.end_time_value
JOIN seasons s ON s.season_name = 'Winter 2024'
JOIN competitions c ON c.competition_id = s.competition_id
JOIN organisations o ON o.organisation_id = c.organisation_id
JOIN season_days sd ON sd.season_id = s.season_id
JOIN users u ON u.email = 'samuel@whitelinegroup.com.au'
WHERE sd.season_day_name = 'SATURDAY'
    AND c.competition_name = 'Junior Domestic'
    AND o.organisation_name = 'Kilsyth Basketball Association';


COMMIT;
