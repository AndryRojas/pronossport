-- =====================================================
-- BASE DE DATOS: raw_pronossport
-- Descripción: Almacena datos crudos de las APIs externas
-- =====================================================

CREATE DATABASE IF NOT EXISTS raw_pronossport;
USE raw_pronossport;

-- =====================================================
-- TABLAS COMUNES PARA TODOS LOS DEPORTES (DATOS CRUDOS)
-- =====================================================

-- Tabla de deportes (catálogo básico)
CREATE TABLE IF NOT EXISTS sports_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    external_id VARCHAR(50),
    name VARCHAR(50) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    api_source VARCHAR(50),
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_external (external_id)
);

-- Ligas/Competiciones crudas
CREATE TABLE IF NOT EXISTS leagues_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sport_code VARCHAR(20) NOT NULL,
    external_id VARCHAR(50),
    name VARCHAR(100),
    country VARCHAR(50),
    country_code VARCHAR(10),
    season VARCHAR(20),
    season_start DATE,
    season_end DATE,
    logo_url VARCHAR(500),
    flag_url VARCHAR(500),
    api_source VARCHAR(50),
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sport_external (sport_code, external_id),
    INDEX idx_season (season),
    INDEX idx_created (created_at)
);

-- Equipos crudos
CREATE TABLE IF NOT EXISTS teams_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sport_code VARCHAR(20) NOT NULL,
    external_id VARCHAR(50),
    name VARCHAR(100),
    code VARCHAR(20),
    country VARCHAR(50),
    country_code VARCHAR(10),
    founded_year INT,
    logo_url VARCHAR(500),
    venue_name VARCHAR(200),
    venue_address VARCHAR(500),
    venue_city VARCHAR(100),
    venue_capacity INT,
    venue_surface VARCHAR(50),
    venue_image_url VARCHAR(500),
    api_source VARCHAR(50),
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sport_external (sport_code, external_id),
    INDEX idx_name (name),
    INDEX idx_created (created_at)
);

-- Jugadores crudos
CREATE TABLE IF NOT EXISTS players_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sport_code VARCHAR(20) NOT NULL,
    external_id VARCHAR(50),
    external_team_id VARCHAR(50),
    name VARCHAR(100),
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    birth_date DATE,
    birth_place VARCHAR(100),
    birth_country VARCHAR(50),
    nationality VARCHAR(50),
    position VARCHAR(50),
    photo_url VARCHAR(500),
    height VARCHAR(20),
    weight VARCHAR(20),
    number INT,
    api_source VARCHAR(50),
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sport_external (sport_code, external_id),
    INDEX idx_team (external_team_id),
    INDEX idx_name (name),
    INDEX idx_created (created_at)
);

-- =====================================================
-- TABLAS ESPECÍFICAS DE FÚTBOL (DATOS CRUDOS)
-- =====================================================

-- Partidos de fútbol crudos
CREATE TABLE IF NOT EXISTS football_matches_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    external_id VARCHAR(50) UNIQUE,
    external_league_id VARCHAR(50),
    season VARCHAR(20),
    round VARCHAR(50),
    match_date DATETIME,
    timestamp_unix BIGINT,
    timezone VARCHAR(50),
    status_long VARCHAR(50),
    status_short VARCHAR(10),
    status_elapsed INT,
    venue_id VARCHAR(50),
    venue_name VARCHAR(200),
    venue_city VARCHAR(100),
    referee VARCHAR(100),
    
    -- Equipos
    home_team_external_id VARCHAR(50),
    home_team_name VARCHAR(100),
    home_team_logo VARCHAR(500),
    away_team_external_id VARCHAR(50),
    away_team_name VARCHAR(100),
    away_team_logo VARCHAR(500),
    
    -- Marcador
    home_score INT,
    away_score INT,
    home_score_halftime INT,
    away_score_halftime INT,
    home_score_fulltime INT,
    away_score_fulltime INT,
    home_score_extratime INT,
    away_score_extratime INT,
    home_score_penalty INT,
    away_score_penalty INT,
    
    -- Metadatos
    api_source VARCHAR(50),
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_external (external_id),
    INDEX idx_date (match_date),
    INDEX idx_teams (home_team_external_id, away_team_external_id),
    INDEX idx_league_season (external_league_id, season),
    INDEX idx_status (status_short),
    INDEX idx_created (created_at)
);

-- Estadísticas de partidos crudas
CREATE TABLE IF NOT EXISTS football_match_statistics_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    external_match_id VARCHAR(50),
    external_team_id VARCHAR(50),
    
    -- Estadísticas generales
    shots_total INT,
    shots_on_goal INT,
    shots_off_goal INT,
    shots_blocked INT,
    shots_inside_box INT,
    shots_outside_box INT,
    
    -- Pases
    passes_total INT,
    passes_accurate INT,
    passes_percentage DECIMAL(5,2),
    
    -- Posesión y control
    possession_percentage DECIMAL(5,2),
    ball_possession INT,
    
    -- Faltas y tarjetas
    fouls INT,
    corners INT,
    offsides INT,
    yellow_cards INT,
    red_cards INT,
    
    -- Portero
    goalkeeper_saves INT,
    
    -- Estadísticas adicionales
    total_passes INT,
    passes_completed INT,
    attacks INT,
    dangerous_attacks INT,
    
    -- Metadatos
    api_source VARCHAR(50),
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_match_team (external_match_id, external_team_id),
    INDEX idx_created (created_at)
);

-- Eventos de partidos (goles, tarjetas, sustituciones)
CREATE TABLE IF NOT EXISTS football_match_events_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    external_match_id VARCHAR(50),
    external_team_id VARCHAR(50),
    external_player_id VARCHAR(50),
    external_assist_id VARCHAR(50),
    time_elapsed INT,
    time_extra INT,
    event_type VARCHAR(50), -- 'Goal', 'Card', 'Subst', 'Var'
    event_detail VARCHAR(100), -- 'Normal Goal', 'Yellow Card', etc.
    comments TEXT,
    
    -- Metadatos
    api_source VARCHAR(50),
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_match (external_match_id),
    INDEX idx_type (event_type),
    INDEX idx_player (external_player_id),
    INDEX idx_created (created_at)
);

-- Alineaciones de partidos
CREATE TABLE IF NOT EXISTS football_match_lineups_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    external_match_id VARCHAR(50),
    external_team_id VARCHAR(50),
    external_player_id VARCHAR(50),
    player_name VARCHAR(100),
    player_number INT,
    player_position VARCHAR(50),
    player_grid VARCHAR(10),
    is_starter BOOLEAN,
    
    -- Metadatos
    api_source VARCHAR(50),
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_match_team (external_match_id, external_team_id),
    INDEX idx_player (external_player_id),
    INDEX idx_created (created_at)
);

-- Estadísticas de jugadores por partido
CREATE TABLE IF NOT EXISTS football_player_match_stats_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    external_match_id VARCHAR(50),
    external_team_id VARCHAR(50),
    external_player_id VARCHAR(50),
    
    -- Tiempo jugado
    minutes_played INT,
    substitute BOOLEAN,
    
    -- Rendimiento
    rating DECIMAL(3,1),
    captain BOOLEAN,
    
    -- Goles y asistencias
    goals INT,
    assists INT,
    
    -- Tiros
    shots_total INT,
    shots_on_target INT,
    
    -- Pases
    passes_total INT,
    passes_accuracy INT,
    passes_key INT,
    
    -- Regates
    dribbles_attempted INT,
    dribbles_success INT,
    dribbles_past INT,
    
    -- Defensa
    tackles_total INT,
    tackles_blocks INT,
    tackles_interceptions INT,
    
    -- Duelos
    duels_total INT,
    duels_won INT,
    
    -- Faltas
    fouls_committed INT,
    fouls_drawn INT,
    
    -- Tarjetas
    cards_yellow INT,
    cards_red INT,
    
    -- Penaltis
    penalty_scored INT,
    penalty_missed INT,
    penalty_saved INT,
    penalty_committed INT,
    penalty_won INT,
    
    -- Metadatos
    api_source VARCHAR(50),
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_match_player (external_match_id, external_player_id),
    INDEX idx_team (external_team_id),
    INDEX idx_created (created_at)
);

-- Odds/Cuotas de apuestas crudas
CREATE TABLE IF NOT EXISTS football_odds_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    external_match_id VARCHAR(50),
    external_bookmaker_id VARCHAR(50),
    bookmaker_name VARCHAR(100),
    
    -- Fecha de actualización de odds
    odds_date DATETIME,
    
    -- 1X2 Market
    market_1x2_home DECIMAL(6,3),
    market_1x2_draw DECIMAL(6,3),
    market_1x2_away DECIMAL(6,3),
    
    -- Over/Under 2.5
    over_2_5 DECIMAL(6,3),
    under_2_5 DECIMAL(6,3),
    
    -- Both Teams to Score
    btts_yes DECIMAL(6,3),
    btts_no DECIMAL(6,3),
    
    -- Asian Handicap
    ah_line DECIMAL(4,2),
    ah_home DECIMAL(6,3),
    ah_away DECIMAL(6,3),
    
    -- Correct Score (principales)
    cs_0_0 DECIMAL(8,3),
    cs_1_0 DECIMAL(8,3),
    cs_0_1 DECIMAL(8,3),
    cs_1_1 DECIMAL(8,3),
    cs_2_0 DECIMAL(8,3),
    cs_0_2 DECIMAL(8,3),
    cs_2_1 DECIMAL(8,3),
    cs_1_2 DECIMAL(8,3),
    cs_2_2 DECIMAL(8,3),
    
    -- Metadatos
    api_source VARCHAR(50),
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_match (external_match_id),
    INDEX idx_bookmaker (external_bookmaker_id),
    INDEX idx_date (odds_date),
    INDEX idx_created (created_at)
);

-- Standings/Clasificación
CREATE TABLE IF NOT EXISTS football_standings_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    external_league_id VARCHAR(50),
    season VARCHAR(20),
    external_team_id VARCHAR(50),
    
    -- Posición y datos
    rank_position INT,
    points INT,
    goals_diff INT,
    group_name VARCHAR(50),
    form VARCHAR(10),
    status VARCHAR(50),
    description VARCHAR(200),
    
    -- Estadísticas generales
    played INT,
    win INT,
    draw INT,
    lose INT,
    goals_for INT,
    goals_against INT,
    
    -- Local
    home_played INT,
    home_win INT,
    home_draw INT,
    home_lose INT,
    home_goals_for INT,
    home_goals_against INT,
    
    -- Visitante
    away_played INT,
    away_win INT,
    away_draw INT,
    away_lose INT,
    away_goals_for INT,
    away_goals_against INT,
    
    -- Fecha de actualización
    update_date DATE,
    
    -- Metadatos
    api_source VARCHAR(50),
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_league_season (external_league_id, season),
    INDEX idx_team (external_team_id),
    INDEX idx_update (update_date),
    INDEX idx_created (created_at)
);

-- =====================================================
-- TABLAS PARA OTROS DEPORTES (ESTRUCTURA SIMILAR)
-- =====================================================

-- Baloncesto
CREATE TABLE IF NOT EXISTS basketball_matches_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    external_id VARCHAR(50) UNIQUE,
    -- Estructura similar a football pero con quarters
    home_score_q1 INT,
    home_score_q2 INT,
    home_score_q3 INT,
    home_score_q4 INT,
    home_score_ot INT,
    away_score_q1 INT,
    away_score_q2 INT,
    away_score_q3 INT,
    away_score_q4 INT,
    away_score_ot INT,
    -- ... resto de campos similares
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_external (external_id)
);

-- Tenis
CREATE TABLE IF NOT EXISTS tennis_matches_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    external_id VARCHAR(50) UNIQUE,
    -- Estructura para sets y games
    player1_external_id VARCHAR(50),
    player2_external_id VARCHAR(50),
    sets_player1 INT,
    sets_player2 INT,
    -- ... detalles de cada set
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_external (external_id)
);

-- =====================================================
-- TABLAS DE CONTROL Y LOGS
-- =====================================================

-- Control de sincronización con APIs
CREATE TABLE IF NOT EXISTS api_sync_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    api_source VARCHAR(50),
    endpoint VARCHAR(200),
    sport_code VARCHAR(20),
    sync_type VARCHAR(50), -- 'leagues', 'teams', 'matches', etc.
    sync_date DATETIME,
    records_fetched INT,
    records_processed INT,
    status VARCHAR(20), -- 'success', 'partial', 'failed'
    error_message TEXT,
    execution_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_source (api_source),
    INDEX idx_sport (sport_code),
    INDEX idx_date (sync_date),
    INDEX idx_status (status)
);

-- Log de errores de procesamiento
CREATE TABLE IF NOT EXISTS processing_errors_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    table_name VARCHAR(100),
    record_external_id VARCHAR(50),
    error_type VARCHAR(100),
    error_message TEXT,
    raw_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_table (table_name),
    INDEX idx_created (created_at)
);