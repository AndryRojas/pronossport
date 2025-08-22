from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, BigInteger, Boolean, DECIMAL, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

RawBase = declarative_base()

class RawAPIData(RawBase):
    __tablename__ = 'raw_api_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String(255), nullable=False)
    raw_data = Column(JSON, nullable=False)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    api_response_code = Column(Integer)
    request_params = Column(JSON)
    
    def __repr__(self):
        return f"<RawAPIData(id={self.id}, endpoint='{self.endpoint}', extracted_at='{self.extracted_at}')>"

class RawMatchData(RawBase):
    __tablename__ = 'raw_matches'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(100), nullable=False, unique=True)
    raw_json = Column(JSON, nullable=False)
    source_endpoint = Column(String(255))
    extracted_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Integer, default=0)  # 0 = no procesado, 1 = procesado
    
    def __repr__(self):
        return f"<RawMatchData(id={self.id}, external_id='{self.external_id}', processed={self.processed})>"

class RawTeamData(RawBase):
    __tablename__ = 'raw_teams'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(100), nullable=False, unique=True)
    raw_json = Column(JSON, nullable=False)
    source_endpoint = Column(String(255))
    extracted_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<RawTeamData(id={self.id}, external_id='{self.external_id}', processed={self.processed})>"

# Tablas adicionales basadas en el script SQL

class SportsRaw(RawBase):
    __tablename__ = 'sports_raw'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(50))
    name = Column(String(50), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    api_source = Column(String(50))
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class LeaguesRaw(RawBase):
    __tablename__ = 'leagues_raw'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sport_code = Column(String(20), nullable=False)
    external_id = Column(String(50))
    name = Column(String(100))
    country = Column(String(50))
    country_code = Column(String(10))
    season = Column(String(20))
    season_start = Column(Date)
    season_end = Column(Date)
    logo_url = Column(String(500))
    flag_url = Column(String(500))
    api_source = Column(String(50))
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

class TeamsRaw(RawBase):
    __tablename__ = 'teams_raw'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sport_code = Column(String(20), nullable=False)
    external_id = Column(String(50))
    name = Column(String(100))
    code = Column(String(20))
    country = Column(String(50))
    country_code = Column(String(10))
    founded_year = Column(Integer)
    logo_url = Column(String(500))
    venue_name = Column(String(200))
    venue_address = Column(String(500))
    venue_city = Column(String(100))
    venue_capacity = Column(Integer)
    venue_surface = Column(String(50))
    venue_image_url = Column(String(500))
    api_source = Column(String(50))
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extracted_for_league = Column(String(10))	
    extracted_for_season = Column(String(4))

class PlayersRaw(RawBase):
    __tablename__ = 'players_raw'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sport_code = Column(String(20), nullable=False)
    external_id = Column(String(50))
    external_team_id = Column(String(50))
    external_league_id = Column(String(50))
    season = Column(String(4))
    name = Column(String(100))
    firstname = Column(String(50))
    lastname = Column(String(50))
    birth_date = Column(Date)
    birth_place = Column(String(100))
    birth_country = Column(String(50))
    nationality = Column(String(50))
    position = Column(String(50))
    photo_url = Column(String(500))
    height = Column(String(20))
    weight = Column(String(20))
    number = Column(Integer)
    api_source = Column(String(50))
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FootballMatchesRaw(RawBase):
    __tablename__ = 'football_matches_raw'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(50), unique=True)
    external_league_id = Column(String(50))
    season = Column(String(20))
    round = Column(String(50))
    match_date = Column(DateTime)
    timestamp_unix = Column(BigInteger)
    timezone = Column(String(50))
    status_long = Column(String(50))
    status_short = Column(String(10))
    status_elapsed = Column(Integer)
    venue_id = Column(String(50))
    venue_name = Column(String(200))
    venue_city = Column(String(100))
    referee = Column(String(100))
    
    # Equipos
    home_team_external_id = Column(String(50))
    home_team_name = Column(String(100))
    home_team_logo = Column(String(500))
    away_team_external_id = Column(String(50))
    away_team_name = Column(String(100))
    away_team_logo = Column(String(500))
    
    # Marcador
    home_score = Column(Integer)
    away_score = Column(Integer)
    home_score_halftime = Column(Integer)
    away_score_halftime = Column(Integer)
    home_score_fulltime = Column(Integer)
    away_score_fulltime = Column(Integer)
    home_score_extratime = Column(Integer)
    away_score_extratime = Column(Integer)
    home_score_penalty = Column(Integer)
    away_score_penalty = Column(Integer)
    
    # Metadatos
    api_source = Column(String(50))
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FootballMatchStatisticsRaw(RawBase):
    __tablename__ = 'football_match_statistics_raw'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_match_id = Column(String(50))
    external_team_id = Column(String(50))
    
    # Estadísticas generales
    shots_total = Column(Integer)
    shots_on_goal = Column(Integer)
    shots_off_goal = Column(Integer)
    shots_blocked = Column(Integer)
    shots_inside_box = Column(Integer)
    shots_outside_box = Column(Integer)
    
    # Pases
    passes_total = Column(Integer)
    passes_accurate = Column(Integer)
    passes_percentage = Column(DECIMAL(5,2))
    
    # Posesión y control
    possession_percentage = Column(DECIMAL(5,2))
    ball_possession = Column(Integer)
    
    # Faltas y tarjetas
    fouls = Column(Integer)
    corners = Column(Integer)
    offsides = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    
    # Portero
    goalkeeper_saves = Column(Integer)
    
    # Estadísticas adicionales
    total_passes = Column(Integer)
    passes_completed = Column(Integer)
    attacks = Column(Integer)
    dangerous_attacks = Column(Integer)
    
    # Metadatos
    api_source = Column(String(50))
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class FootballMatchEventsRaw(RawBase):
    __tablename__ = 'football_match_events_raw'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_match_id = Column(String(50))
    external_team_id = Column(String(50))
    external_player_id = Column(String(50))
    external_assist_id = Column(String(50))
    time_elapsed = Column(Integer)
    time_extra = Column(Integer)
    event_type = Column(String(50))  # 'Goal', 'Card', 'Subst', 'Var'
    event_detail = Column(String(100))  # 'Normal Goal', 'Yellow Card', etc.
    comments = Column(Text)
    
    # Metadatos
    api_source = Column(String(50))
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class FootballMatchLineupsRaw(RawBase):
    __tablename__ = 'football_match_lineups_raw'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_match_id = Column(String(50))
    external_team_id = Column(String(50))
    external_player_id = Column(String(50))
    player_name = Column(String(100))
    player_number = Column(Integer)
    player_position = Column(String(50))
    player_grid = Column(String(10))
    is_starter = Column(Boolean)
    
    # Metadatos
    api_source = Column(String(50))
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class FootballPlayerSeasonStatsRaw(RawBase):
    __tablename__ = 'football_player_season_stats_raw'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_player_id = Column(String(50))
    external_team_id = Column(String(50))
    external_league_id = Column(String(50))
    season = Column(String(4))
    
    # Estadísticas de temporada
    appearances = Column(Integer)
    lineups = Column(Integer)
    minutes = Column(Integer)
    number = Column(Integer)
    position = Column(String(50))
    rating = Column(DECIMAL(4,2))
    captain = Column(Boolean)
    
    # Goles y asistencias
    goals_total = Column(Integer)
    goals_conceded = Column(Integer)
    assists = Column(Integer)
    saves = Column(Integer)
    
    # Tiros
    shots_total = Column(Integer)
    shots_on = Column(Integer)
    
    # Pases
    passes_total = Column(Integer)
    passes_key = Column(Integer)
    passes_accuracy = Column(Integer)
    
    # Tackles
    tackles_total = Column(Integer)
    tackles_blocks = Column(Integer)
    tackles_interceptions = Column(Integer)
    
    # Duelos
    duels_total = Column(Integer)
    duels_won = Column(Integer)
    
    # Regates
    dribbles_attempts = Column(Integer)
    dribbles_success = Column(Integer)
    dribbles_past = Column(Integer)
    
    # Faltas
    fouls_drawn = Column(Integer)
    fouls_committed = Column(Integer)
    
    # Tarjetas
    cards_yellow = Column(Integer)
    cards_yellowred = Column(Integer)
    cards_red = Column(Integer)
    
    # Penaltis
    penalty_won = Column(Integer)
    penalty_committed = Column(Integer)
    penalty_scored = Column(Integer)
    penalty_missed = Column(Integer)
    penalty_saved = Column(Integer)
    
    # Metadatos
    api_source = Column(String(50))
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FootballPlayerMatchStatsRaw(RawBase):
    __tablename__ = 'football_player_match_stats_raw'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_match_id = Column(String(50))
    external_team_id = Column(String(50))
    external_player_id = Column(String(50))
    
    # Tiempo jugado
    minutes_played = Column(Integer)
    substitute = Column(Boolean)
    
    # Rendimiento
    rating = Column(DECIMAL(3,1))
    captain = Column(Boolean)
    
    # Goles y asistencias
    goals = Column(Integer)
    assists = Column(Integer)
    
    # Tiros
    shots_total = Column(Integer)
    shots_on_target = Column(Integer)
    
    # Pases
    passes_total = Column(Integer)
    passes_accuracy = Column(Integer)
    passes_key = Column(Integer)
    
    # Regates
    dribbles_attempted = Column(Integer)
    dribbles_success = Column(Integer)
    dribbles_past = Column(Integer)
    
    # Defensa
    tackles_total = Column(Integer)
    tackles_blocks = Column(Integer)
    tackles_interceptions = Column(Integer)
    
    # Duelos
    duels_total = Column(Integer)
    duels_won = Column(Integer)
    
    # Faltas
    fouls_committed = Column(Integer)
    fouls_drawn = Column(Integer)
    
    # Tarjetas
    cards_yellow = Column(Integer)
    cards_red = Column(Integer)
    
    # Penaltis
    penalty_scored = Column(Integer)
    penalty_missed = Column(Integer)
    penalty_saved = Column(Integer)
    penalty_committed = Column(Integer)
    penalty_won = Column(Integer)
    
    # Metadatos
    api_source = Column(String(50))
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class FootballOddsRaw(RawBase):
    __tablename__ = 'football_odds_raw'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_match_id = Column(String(50))
    external_bookmaker_id = Column(String(50))
    bookmaker_name = Column(String(100))
    
    # Fecha de actualización de odds
    odds_date = Column(DateTime)
    
    # 1X2 Market
    market_1x2_home = Column(DECIMAL(6,3))
    market_1x2_draw = Column(DECIMAL(6,3))
    market_1x2_away = Column(DECIMAL(6,3))
    
    # Over/Under 2.5
    over_2_5 = Column(DECIMAL(6,3))
    under_2_5 = Column(DECIMAL(6,3))
    
    # Both Teams to Score
    btts_yes = Column(DECIMAL(6,3))
    btts_no = Column(DECIMAL(6,3))
    
    # Asian Handicap
    ah_line = Column(DECIMAL(4,2))
    ah_home = Column(DECIMAL(6,3))
    ah_away = Column(DECIMAL(6,3))
    
    # Correct Score (principales)
    cs_0_0 = Column(DECIMAL(8,3))
    cs_1_0 = Column(DECIMAL(8,3))
    cs_0_1 = Column(DECIMAL(8,3))
    cs_1_1 = Column(DECIMAL(8,3))
    cs_2_0 = Column(DECIMAL(8,3))
    cs_0_2 = Column(DECIMAL(8,3))
    cs_2_1 = Column(DECIMAL(8,3))
    cs_1_2 = Column(DECIMAL(8,3))
    cs_2_2 = Column(DECIMAL(8,3))
    
    # Metadatos
    api_source = Column(String(50))
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class FootballStandingsRaw(RawBase):
    __tablename__ = 'football_standings_raw'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_league_id = Column(String(50))
    season = Column(String(20))
    external_team_id = Column(String(50))
    
    # Posición y datos
    rank_position = Column(Integer)
    points = Column(Integer)
    goals_diff = Column(Integer)
    group_name = Column(String(50))
    form = Column(String(10))
    status = Column(String(50))
    description = Column(String(200))
    
    # Estadísticas generales
    played = Column(Integer)
    win = Column(Integer)
    draw = Column(Integer)
    lose = Column(Integer)
    goals_for = Column(Integer)
    goals_against = Column(Integer)
    
    # Local
    home_played = Column(Integer)
    home_win = Column(Integer)
    home_draw = Column(Integer)
    home_lose = Column(Integer)
    home_goals_for = Column(Integer)
    home_goals_against = Column(Integer)
    
    # Visitante
    away_played = Column(Integer)
    away_win = Column(Integer)
    away_draw = Column(Integer)
    away_lose = Column(Integer)
    away_goals_for = Column(Integer)
    away_goals_against = Column(Integer)
    
    # Fecha de actualización
    update_date = Column(Date)
    
    # Metadatos
    api_source = Column(String(50))
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class ApiSyncLog(RawBase):
    __tablename__ = 'api_sync_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_source = Column(String(50))
    endpoint = Column(String(200))
    sport_code = Column(String(20))
    sync_type = Column(String(50))  # 'leagues', 'teams', 'matches', etc.
    sync_date = Column(DateTime)
    records_fetched = Column(Integer)
    records_processed = Column(Integer)
    status = Column(String(20))  # 'success', 'partial', 'failed'
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProcessingErrorsLog(RawBase):
    __tablename__ = 'processing_errors_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(100))
    record_external_id = Column(String(50))
    error_type = Column(String(100))
    error_message = Column(Text)
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExtractionLog(RawBase):
    __tablename__ = 'extraction_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String(255), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String(50))  # 'success', 'error', 'partial'
    records_extracted = Column(Integer, default=0)
    error_message = Column(Text)
    
    def __repr__(self):
        return f"<ExtractionLog(id={self.id}, endpoint='{self.endpoint}', status='{self.status}')>"