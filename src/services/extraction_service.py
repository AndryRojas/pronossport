from typing import List, Dict, Any, Optional
from datetime import datetime
from src.api.client import APIClient
from src.database.connection import raw_db_manager
from src.models.raw_models import (RawAPIData, RawMatchData, RawTeamData, ExtractionLog,
                                   FootballMatchesRaw, TeamsRaw, LeaguesRaw, FootballStandingsRaw,
                                   FootballMatchStatisticsRaw, FootballMatchEventsRaw, FootballMatchLineupsRaw,
                                   FootballPlayerMatchStatsRaw, FootballOddsRaw, ApiSyncLog, PlayersRaw,
                                   FootballPlayerSeasonStatsRaw)
from src.config.settings import settings
from loguru import logger

class ExtractionService:
    def __init__(self):
        self.api_client = APIClient()
    
    def extract_and_store(self, endpoint: str, params: Optional[Dict] = None, 
                         model_class = RawAPIData) -> bool:
        extraction_log = ExtractionLog(
            endpoint=endpoint,
            start_time=datetime.utcnow(),
            status='running'
        )
        
        try:
            with raw_db_manager.get_session() as session:
                session.add(extraction_log)
                session.commit()
                
                # Extraer datos de la API
                data = self.api_client.get(endpoint, params)
                
                if not data:
                    extraction_log.status = 'error'
                    extraction_log.error_message = 'No data received from API'
                    extraction_log.end_time = datetime.utcnow()
                    session.commit()
                    return False
                
                # Guardar datos según el tipo
                records_saved = 0
                
                if model_class == RawAPIData:
                    records_saved = self._save_generic_data(session, endpoint, data, params)
                elif model_class == RawMatchData:
                    records_saved = self._save_match_data(session, endpoint, data)
                elif model_class == RawTeamData:
                    records_saved = self._save_team_data(session, endpoint, data)
                
                # Actualizar log de extracción
                extraction_log.status = 'success'
                extraction_log.records_extracted = records_saved
                extraction_log.end_time = datetime.utcnow()
                session.commit()
                
                logger.info(f"Extracción exitosa: {records_saved} registros de {endpoint}")
                return True
                
        except Exception as e:
            logger.error(f"Error en extracción de {endpoint}: {e}")
            with raw_db_manager.get_session() as session:
                extraction_log.status = 'error'
                extraction_log.error_message = str(e)
                extraction_log.end_time = datetime.utcnow()
                session.commit()
            return False
    
    def _save_generic_data(self, session, endpoint: str, data: Any, params: Optional[Dict]) -> int:
        raw_record = RawAPIData(
            endpoint=endpoint,
            raw_data=data,
            request_params=params,
            api_response_code=200
        )
        session.add(raw_record)
        return 1
    
    def _save_match_data(self, session, endpoint: str, data: Any) -> int:
        records_saved = 0
        
        # Asumiendo que data es una lista de partidos o un objeto con lista de partidos
        matches = data if isinstance(data, list) else data.get('matches', [data])
        
        for match in matches:
            external_id = str(match.get('id', match.get('match_id', f"unknown_{records_saved}")))
            
            # Verificar si ya existe
            existing = session.query(RawMatchData).filter_by(external_id=external_id).first()
            if existing:
                # Actualizar datos existentes
                existing.raw_json = match
                existing.extracted_at = datetime.utcnow()
                existing.processed = 0  # Marcar para reprocesar
            else:
                # Crear nuevo registro
                raw_match = RawMatchData(
                    external_id=external_id,
                    raw_json=match,
                    source_endpoint=endpoint
                )
                session.add(raw_match)
            
            records_saved += 1
        
        return records_saved
    
    def _save_team_data(self, session, endpoint: str, data: Any) -> int:
        records_saved = 0
        
        # Asumiendo que data es una lista de equipos o un objeto con lista de equipos
        teams = data if isinstance(data, list) else data.get('teams', [data])
        
        for team in teams:
            external_id = str(team.get('id', team.get('team_id', f"unknown_{records_saved}")))
            
            # Verificar si ya existe
            existing = session.query(RawTeamData).filter_by(external_id=external_id).first()
            if existing:
                # Actualizar datos existentes
                existing.raw_json = team
                existing.extracted_at = datetime.utcnow()
                existing.processed = 0  # Marcar para reprocesar
            else:
                # Crear nuevo registro
                raw_team = RawTeamData(
                    external_id=external_id,
                    raw_json=team,
                    source_endpoint=endpoint
                )
                session.add(raw_team)
            
            records_saved += 1
        
        return records_saved
    
    def extract_matches(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> bool:
        params = {}
        if date_from:
            params['from'] = date_from
        if date_to:
            params['to'] = date_to
        
        return self.extract_and_store('matches', params, RawMatchData)
    
    def extract_teams(self, league: Optional[str] = None) -> bool:
        params = {}
        if league:
            params['league'] = league
        
        return self.extract_and_store('teams', params, RawTeamData)
    
    def extract_paginated_matches(self, max_pages: int = 10) -> bool:
        try:
            all_matches = self.api_client.get_paginated_data('matches', max_pages=max_pages)
            
            if not all_matches:
                logger.warning("No se obtuvieron partidos de la paginación")
                return False
            
            # Guardar todos los partidos
            with raw_db_manager.get_session() as session:
                records_saved = self._save_match_data(session, 'matches_paginated', all_matches)
                logger.info(f"Guardados {records_saved} partidos via paginación")
                return True
                
        except Exception as e:
            logger.error(f"Error en extracción paginada: {e}")
            return False
    
    # Métodos específicos para API-Sports
    
    def extract_football_fixtures(self, date: Optional[str] = None, league: Optional[int] = None, 
                                 season: Optional[int] = None, date_from: Optional[str] = None, 
                                 date_to: Optional[str] = None) -> bool:
        """Extrae partidos de fútbol de API-Sports"""
        try:
            data = self.api_client.get_fixtures(
                date=date, league=league, season=season, 
                date_from=date_from, date_to=date_to
            )
            
            if not data or 'response' not in data:
                logger.warning("No se obtuvieron datos de fixtures de API-Sports")
                return False
            
            with raw_db_manager.get_session() as session:
                records_saved = 0
                
                for fixture in data['response']:
                    # Mapear datos de API-Sports al modelo
                    match_record = FootballMatchesRaw(
                        external_id=str(fixture['fixture']['id']),
                        external_league_id=str(fixture['league']['id']),
                        season=str(fixture['league']['season']),
                        round=fixture['league']['round'],
                        match_date=datetime.fromtimestamp(fixture['fixture']['timestamp']),
                        timestamp_unix=fixture['fixture']['timestamp'],
                        timezone=fixture['fixture']['timezone'],
                        status_long=fixture['fixture']['status']['long'],
                        status_short=fixture['fixture']['status']['short'],
                        status_elapsed=fixture['fixture']['status']['elapsed'],
                        venue_id=str(fixture['fixture']['venue']['id']) if fixture['fixture']['venue'] else None,
                        venue_name=fixture['fixture']['venue']['name'] if fixture['fixture']['venue'] else None,
                        venue_city=fixture['fixture']['venue']['city'] if fixture['fixture']['venue'] else None,
                        referee=fixture['fixture']['referee'],
                        
                        # Equipos
                        home_team_external_id=str(fixture['teams']['home']['id']),
                        home_team_name=fixture['teams']['home']['name'],
                        home_team_logo=fixture['teams']['home']['logo'],
                        away_team_external_id=str(fixture['teams']['away']['id']),
                        away_team_name=fixture['teams']['away']['name'],
                        away_team_logo=fixture['teams']['away']['logo'],
                        
                        # Marcador
                        home_score=fixture['goals']['home'],
                        away_score=fixture['goals']['away'],
                        home_score_halftime=fixture['score']['halftime']['home'],
                        away_score_halftime=fixture['score']['halftime']['away'],
                        home_score_fulltime=fixture['score']['fulltime']['home'],
                        away_score_fulltime=fixture['score']['fulltime']['away'],
                        home_score_extratime=fixture['score']['extratime']['home'],
                        away_score_extratime=fixture['score']['extratime']['away'],
                        home_score_penalty=fixture['score']['penalty']['home'],
                        away_score_penalty=fixture['score']['penalty']['away'],
                        
                        # Metadatos
                        api_source='api-sports',
                        raw_json=fixture
                    )
                    
                    # Verificar si ya existe
                    existing = session.query(FootballMatchesRaw).filter_by(
                        external_id=str(fixture['fixture']['id'])
                    ).first()
                    
                    if existing:
                        # Actualizar registro existente
                        for key, value in match_record.__dict__.items():
                            if not key.startswith('_'):
                                setattr(existing, key, value)
                        existing.updated_at = datetime.utcnow()
                    else:
                        session.add(match_record)
                    
                    records_saved += 1
                
                session.commit()
                logger.info(f"Guardados {records_saved} partidos de fútbol de API-Sports")
                return True
                
        except Exception as e:
            logger.error(f"Error extrayendo fixtures de fútbol: {e}")
            return False
    
    def extract_football_teams(self, league: Optional[int] = None, season: Optional[int] = None) -> bool:
        """Extrae equipos de fútbol de API-Sports"""
        try:
            data = self.api_client.get_teams(league=league, season=season)
            
            if not data or 'response' not in data:
                logger.warning("No se obtuvieron datos de equipos de API-Sports")
                return False
            
            with raw_db_manager.get_session() as session:
                records_saved = 0
                
                for team_data in data['response']:
                    team = team_data['team']
                    venue = team_data['venue']
                    
                    team_record = TeamsRaw(
                        sport_code='football',
                        external_id=str(team['id']),
                        name=team['name'],
                        code=team['code'],
                        country=team['country'],
                        founded_year=team['founded'],
                        logo_url=team['logo'],
                        venue_name=venue['name'] if venue else None,
                        venue_address=venue['address'] if venue else None,
                        venue_city=venue['city'] if venue else None,
                        venue_capacity=venue['capacity'] if venue else None,
                        venue_surface=venue['surface'] if venue else None,
                        venue_image_url=venue['image'] if venue else None,
                        api_source='api-sports',
                        raw_json=team_data
                    )
                    
                    # Verificar si ya existe
                    existing = session.query(TeamsRaw).filter_by(
                        sport_code='football',
                        external_id=str(team['id'])
                    ).first()
                    
                    if existing:
                        # Actualizar registro existente
                        for key, value in team_record.__dict__.items():
                            if not key.startswith('_'):
                                setattr(existing, key, value)
                        existing.updated_at = datetime.utcnow()
                    else:
                        session.add(team_record)
                    
                    records_saved += 1
                
                session.commit()
                logger.info(f"Guardados {records_saved} equipos de fútbol de API-Sports")
                return True
                
        except Exception as e:
            logger.error(f"Error extrayendo equipos de fútbol: {e}")
            return False
    
    def extract_football_leagues(self, country: Optional[str] = None, season: Optional[int] = None) -> bool:
        """Extrae ligas de fútbol de API-Sports"""
        try:
            data = self.api_client.get_leagues(country=country, season=season)
            
            if not data or 'response' not in data:
                logger.warning("No se obtuvieron datos de ligas de API-Sports")
                return False
            
            with raw_db_manager.get_session() as session:
                records_saved = 0
                
                for league_data in data['response']:
                    league = league_data['league']
                    country_data = league_data['country']
                    
                    # Puede haber múltiples temporadas
                    seasons = league_data.get('seasons', [])
                    
                    for season_data in seasons:
                        league_record = LeaguesRaw(
                            sport_code='football',
                            external_id=str(league['id']),
                            name=league['name'],
                            country=country_data['name'] if country_data else None,
                            country_code=country_data['code'] if country_data else None,
                            season=str(season_data['year']),
                            season_start=datetime.strptime(season_data['start'], '%Y-%m-%d').date() if season_data['start'] else None,
                            season_end=datetime.strptime(season_data['end'], '%Y-%m-%d').date() if season_data['end'] else None,
                            logo_url=league['logo'],
                            flag_url=country_data['flag'] if country_data else None,
                            api_source='api-sports',
                            raw_json=league_data
                        )
                        
                        # Verificar si ya existe
                        existing = session.query(LeaguesRaw).filter_by(
                            sport_code='football',
                            external_id=str(league['id']),
                            season=str(season_data['year'])
                        ).first()
                        
                        if existing:
                            # Actualizar registro existente
                            for key, value in league_record.__dict__.items():
                                if not key.startswith('_'):
                                    setattr(existing, key, value)
                            existing.updated_at = datetime.utcnow()
                        else:
                            session.add(league_record)
                        
                        records_saved += 1
                
                session.commit()
                logger.info(f"Guardadas {records_saved} ligas de fútbol de API-Sports")
                return True
                
        except Exception as e:
            logger.error(f"Error extrayendo ligas de fútbol: {e}")
            return False
    
    def extract_football_standings(self, league: int, season: int) -> bool:
        """Extrae tabla de posiciones de API-Sports"""
        try:
            data = self.api_client.get_standings(league=league, season=season)
            
            if not data or 'response' not in data:
                logger.warning("No se obtuvieron datos de standings de API-Sports")
                return False
            
            with raw_db_manager.get_session() as session:
                records_saved = 0
                
                for standings_data in data['response']:
                    league_data = standings_data['league']
                    
                    for standings_group in league_data['standings']:
                        for team_standing in standings_group:
                            standing_record = FootballStandingsRaw(
                                external_league_id=str(league),
                                season=str(season),
                                external_team_id=str(team_standing['team']['id']),
                                rank_position=team_standing['rank'],
                                points=team_standing['points'],
                                goals_diff=team_standing['goalsDiff'],
                                group_name=team_standing.get('group'),
                                form=team_standing.get('form'),
                                status=team_standing.get('status'),
                                description=team_standing.get('description'),
                                
                                # Estadísticas generales
                                played=team_standing['all']['played'],
                                win=team_standing['all']['win'],
                                draw=team_standing['all']['draw'],
                                lose=team_standing['all']['lose'],
                                goals_for=team_standing['all']['goals']['for'],
                                goals_against=team_standing['all']['goals']['against'],
                                
                                # Local
                                home_played=team_standing['home']['played'],
                                home_win=team_standing['home']['win'],
                                home_draw=team_standing['home']['draw'],
                                home_lose=team_standing['home']['lose'],
                                home_goals_for=team_standing['home']['goals']['for'],
                                home_goals_against=team_standing['home']['goals']['against'],
                                
                                # Visitante
                                away_played=team_standing['away']['played'],
                                away_win=team_standing['away']['win'],
                                away_draw=team_standing['away']['draw'],
                                away_lose=team_standing['away']['lose'],
                                away_goals_for=team_standing['away']['goals']['for'],
                                away_goals_against=team_standing['away']['goals']['against'],
                                
                                update_date=datetime.now().date(),
                                api_source='api-sports',
                                raw_json=team_standing
                            )
                            
                            # Verificar si ya existe
                            existing = session.query(FootballStandingsRaw).filter_by(
                                external_league_id=str(league),
                                season=str(season),
                                external_team_id=str(team_standing['team']['id'])
                            ).first()
                            
                            if existing:
                                # Actualizar registro existente
                                for key, value in standing_record.__dict__.items():
                                    if not key.startswith('_'):
                                        setattr(existing, key, value)
                            else:
                                session.add(standing_record)
                            
                            records_saved += 1
                
                session.commit()
                logger.info(f"Guardados {records_saved} registros de standings de API-Sports")
                return True
                
        except Exception as e:
            logger.error(f"Error extrayendo standings: {e}")
            return False

    def extract_teams_from_leagues_db(self, country: str = None, league_id: int =0, season_from: int = 2018, season_to: int = 2025) -> bool:
        """
        Extrae equipos de todas las ligas y temporadas guardadas en leagues_raw
        Args:
            country: País de las ligas (ej: 'England')
            season_from: Temporada inicial (ej: 2018)
            season_to: Temporada final (ej: 2025)
        """
        try:
            total_teams_saved = 0
            total_leagues_processed = 0
            
            with raw_db_manager.get_session() as session:
                # Obtener todas las ligas del rango de temporadas
                query = session.query(LeaguesRaw).filter(
                    LeaguesRaw.sport_code == 'football',
                    LeaguesRaw.season.between(str(season_from), str(season_to))
                )
                
                if country:
                    query = query.filter(LeaguesRaw.country == country)
                
                if league_id:
                    query = query.filter(LeaguesRaw.external_id == league_id)

                leagues = query.all()
                
                logger.info(f"🏆 Encontradas {len(leagues)} ligas para extraer equipos")
                logger.info(f"📅 Rango: {season_from} - {season_to}")
                if country:
                    logger.info(f"🌍 País: {country}")
                
                for league in leagues:
                    league_id = int(league.external_id)
                    season = int(league.season)
                    
                    logger.info(f"⚽ Procesando: {league.name} - Temporada {season} (ID: {league_id})")
                    
                    try:
                        # Llamar a la API para obtener equipos de esta liga/temporada
                        data = self.api_client.get_teams(league=league_id, season=season)
                        
                        if not data or 'response' not in data:
                            logger.warning(f"❌ Sin datos para liga {league.name} - {season}")
                            continue
                        
                        teams_in_league = 0
                        
                        for team_data in data['response']:
                            team = team_data['team']
                            venue = team_data['venue']
                            
                            # Crear registro con liga y temporada específica
                            team_record = TeamsRaw(
                                sport_code='football',
                                external_id=str(team['id']),
                                name=team['name'],
                                code=team['code'],
                                country=team['country'],
                                founded_year=team['founded'],
                                logo_url=team['logo'],
                                venue_name=venue['name'] if venue else None,
                                venue_address=venue['address'] if venue else None,
                                venue_city=venue['city'] if venue else None,
                                venue_capacity=venue['capacity'] if venue else None,
                                venue_surface=venue['surface'] if venue else None,
                                venue_image_url=venue['image'] if venue else None,
                                api_source='api-sports',
                                
                                raw_json={
                                    **team_data,
                                    'extracted_for_league': league_id,
                                    'extracted_for_season': season,
                                    'league_name': league.name
                                },
                                extracted_for_league=league_id,
                                extracted_for_season=season
                            )
                            
                            # Verificar si ya existe este equipo
                            existing = session.query(TeamsRaw).filter_by(
                                sport_code='football',
                                external_id=str(team['id']),
                                extracted_for_league= league_id,
                                extracted_for_season= season
                            ).first()
                            
                            if existing:
                                # Actualizar registro existente
                                for key, value in team_record.__dict__.items():
                                    if not key.startswith('_'):
                                        setattr(existing, key, value)
                                existing.updated_at = datetime.utcnow()
                            else:
                                session.add(team_record)
                            
                            teams_in_league += 1
                        
                        session.commit()
                        total_teams_saved += teams_in_league
                        total_leagues_processed += 1
                        
                        logger.info(f"  ✅ {teams_in_league} equipos guardados")
                        
                        # Pausa para no sobrecargar la API
                        import time
                        time.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"❌ Error procesando liga {league.name}: {e}")
                        continue
                
                logger.info(f"🎉 Proceso completado:")
                logger.info(f"  📊 Ligas procesadas: {total_leagues_processed}")
                logger.info(f"  ⚽ Total equipos guardados: {total_teams_saved}")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Error en extracción masiva de equipos: {e}")
            return False
    
    def get_leagues_summary(self, country: str = None) -> bool:
        """Muestra resumen de ligas disponibles en la base de datos"""
        try:
            with raw_db_manager.get_session() as session:
                query = session.query(LeaguesRaw).filter(LeaguesRaw.sport_code == 'football')
                
                if country:
                    query = query.filter(LeaguesRaw.country == country)
                
                leagues = query.all()
                
                # Agrupar por liga y temporadas
                leagues_summary = {}
                for league in leagues:
                    league_name = league.name
                    season = league.season
                    
                    if league_name not in leagues_summary:
                        leagues_summary[league_name] = {
                            'id': league.external_id,
                            'country': league.country,
                            'seasons': []
                        }
                    
                    leagues_summary[league_name]['seasons'].append(season)
                
                logger.info(f"📋 Resumen de ligas {f'en {country}' if country else 'disponibles'}:")
                for league_name, info in leagues_summary.items():
                    seasons_range = f"{min(info['seasons'])} - {max(info['seasons'])}"
                    logger.info(f"  🏆 {league_name} (ID: {info['id']}) | {info['country']} | {seasons_range} | {len(info['seasons'])} temporadas")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo resumen: {e}")
            return False

    def extract_players_by_league_season(self, league_id: int, season: int, team_id: Optional[int] = None) -> bool:
        """
        Extrae jugadores con estadísticas por liga y temporada
        Args:
            league_id: ID de la liga (ej: 39 para Premier League)
            season: Temporada (ej: 2018)
            team_id: ID del equipo específico (opcional)
        """
        try:
            logger.info(f"🏃‍♂️ Extrayendo jugadores de liga {league_id} temporada {season}")
            
            total_players_saved = 0
            page = 21
            total_pages = None
            empty_pages_count = 0
            max_empty_pages = 3  # Máximo de páginas vacías consecutivas antes de parar
            
            with raw_db_manager.get_session() as session:
                while True:
                    # Llamar a la API
                    data = self.api_client.get_players(
                        league=league_id, 
                        season=season, 
                        team=team_id,
                        page=page
                    )
                    
                    if not data or 'response' not in data:
                        logger.warning(f"❌ Sin datos en página {page}")
                        break
                    
                    # Obtener información de paginación de cada respuesta
                    paging_info = data.get('paging', {})
                    api_current_page = paging_info.get('current', page)
                    api_total_pages = paging_info.get('total', 1)
                    results_count = data.get('results', 0)
                    
                    # Usar el total de páginas solo de la primera respuesta válida
                    if total_pages is None and api_total_pages > 1:
                        total_pages = api_total_pages
                    
                    logger.info(f"📄 Procesando página {page}/{total_pages or 'N/A'} (API: {api_current_page}/{api_total_pages}, {results_count} resultados)")
                    
                    players_data = data['response']
                    
                    if not players_data:
                        empty_pages_count += 1
                        logger.info(f"⚠️ No hay jugadores en página {page} ({empty_pages_count}/{max_empty_pages} páginas vacías)")
                        
                        # Solo salir si hay muchas páginas vacías consecutivas Y ya sabemos el total
                        if empty_pages_count >= max_empty_pages and total_pages and page > total_pages:
                            logger.info(f"✅ Deteniendo: {max_empty_pages} páginas vacías consecutivas y superamos total_pages")
                            break
                        
                        # Continuar a la siguiente página
                        page += 1
                        import time
                        time.sleep(2)  # Respetar rate limits
                        continue
                    else:
                        # Resetear contador si encontramos datos
                        empty_pages_count = 0
                    
                    players_in_page = 0
                    players_created = 0
                    players_updated = 0
                    
                    for player_data in players_data:
                        # Información básica del jugador
                        player_info = player_data['player']
                        
                        # Información de estadísticas (puede haber múltiples equipos)
                        statistics_list = player_data.get('statistics', [])
                        
                        for stats in statistics_list:
                            team_info = stats['team']
                            league_info = stats['league']
                            games = stats.get('games', {})
                            goals = stats.get('goals', {})
                            passes = stats.get('passes', {})
                            tackles = stats.get('tackles', {})
                            duels = stats.get('duels', {})
                            dribbles = stats.get('dribbles', {})
                            fouls = stats.get('fouls', {})
                            cards = stats.get('cards', {})
                            penalty = stats.get('penalty', {})
                            shots = stats.get('shots', {})
                            
                            # Crear registro de jugador
                            player_record = PlayersRaw(
                                sport_code='football',
                                external_id=str(player_info['id']),
                                external_team_id=str(team_info['id']),
                                external_league_id=str(league_id),
                                season=str(season),
                                name=player_info.get('name'),
                                firstname=player_info.get('firstname'),
                                lastname=player_info.get('lastname'),
                                birth_date=datetime.strptime(player_info['birth']['date'], '%Y-%m-%d').date() if player_info.get('birth', {}).get('date') else None,
                                birth_place=player_info.get('birth', {}).get('place'),
                                birth_country=player_info.get('birth', {}).get('country'),
                                nationality=player_info.get('nationality'),
                                position=games.get('position'),
                                photo_url=player_info.get('photo'),
                                height=player_info.get('height'),
                                weight=player_info.get('weight'),
                                number=games.get('number'),
                                api_source='api-sports',
                                raw_json=player_data
                            )
                            
                            # Verificar si ya existe
                            existing_player = session.query(PlayersRaw).filter_by(
                                sport_code='football',
                                external_id=str(player_info['id']),
                                external_league_id=str(league_id),
                                season=str(season),
                                external_team_id=str(team_info['id'])
                            ).first()
                            
                            if existing_player:
                                # Actualizar registro existente
                                for key, value in player_record.__dict__.items():
                                    if not key.startswith('_'):
                                        setattr(existing_player, key, value)
                                existing_player.updated_at = datetime.utcnow()
                                players_updated += 1
                            else:
                                session.add(player_record)
                                players_created += 1
                            
                            # Crear registro de estadísticas de temporada
                            season_stats_record = FootballPlayerSeasonStatsRaw(
                                external_player_id=str(player_info['id']),
                                external_team_id=str(team_info['id']),
                                external_league_id=str(league_id),
                                season=str(season),
                                
                                # Estadísticas de temporada
                                appearances=games.get('appearences'),
                                lineups=games.get('lineups'),
                                minutes=games.get('minutes'),
                                number=games.get('number'),
                                position=games.get('position'),
                                rating=float(games.get('rating') or 0) if games.get('rating') else None,
                                captain=games.get('captain', False),
                                
                                # Goles y asistencias
                                goals_total=goals.get('total'),
                                goals_conceded=goals.get('conceded'),
                                assists=goals.get('assists'),
                                saves=goals.get('saves'),
                                
                                # Tiros
                                shots_total=shots.get('total'),
                                shots_on=shots.get('on'),
                                
                                # Pases
                                passes_total=passes.get('total'),
                                passes_key=passes.get('key'),
                                passes_accuracy=passes.get('accuracy'),
                                
                                # Tackles
                                tackles_total=tackles.get('total'),
                                tackles_blocks=tackles.get('blocks'),
                                tackles_interceptions=tackles.get('interceptions'),
                                
                                # Duelos
                                duels_total=duels.get('total'),
                                duels_won=duels.get('won'),
                                
                                # Regates
                                dribbles_attempts=dribbles.get('attempts'),
                                dribbles_success=dribbles.get('success'),
                                dribbles_past=dribbles.get('past'),
                                
                                # Faltas
                                fouls_drawn=fouls.get('drawn'),
                                fouls_committed=fouls.get('committed'),
                                
                                # Tarjetas
                                cards_yellow=cards.get('yellow'),
                                cards_yellowred=cards.get('yellowred'),
                                cards_red=cards.get('red'),
                                
                                # Penaltis
                                penalty_won=penalty.get('won'),
                                penalty_committed=penalty.get('commited'),  # API tiene typo
                                penalty_scored=penalty.get('scored'),
                                penalty_missed=penalty.get('missed'),
                                penalty_saved=penalty.get('saved'),
                                
                                # Metadatos
                                api_source='api-sports',
                                raw_json=stats
                            )
                            
                            # Verificar si ya existen las estadísticas
                            existing_stats = session.query(FootballPlayerSeasonStatsRaw).filter_by(
                                external_player_id=str(player_info['id']),
                                external_team_id=str(team_info['id']),
                                external_league_id=str(league_id),
                                season=str(season)
                            ).first()
                            
                            if existing_stats:
                                # Actualizar registro existente
                                for key, value in season_stats_record.__dict__.items():
                                    if not key.startswith('_'):
                                        setattr(existing_stats, key, value)
                                existing_stats.updated_at = datetime.utcnow()
                            else:
                                session.add(season_stats_record)
                            
                            players_in_page += 1
                    
                    # Realizar commit antes de contar
                    try:
                        session.commit()
                        total_players_saved += players_in_page
                        
                        logger.info(f"  ✅ Página {page}: {players_in_page} jugadores procesados")
                        logger.info(f"    📝 Nuevos: {players_created} | 🔄 Actualizados: {players_updated}")
                    except Exception as commit_error:
                        logger.error(f"❌ Error al hacer commit en página {page}: {commit_error}")
                        session.rollback()
                        break
                    
                    # Verificar si hemos procesado todas las páginas
                    if total_pages and page >= total_pages:
                        logger.info(f"✅ Procesadas todas las páginas ({page}/{total_pages})")
                        break
                    
                    # Pausa para respetar rate limits (6s = ~10 requests/min)
                    import time
                    time.sleep(6)
                    
                    page += 1
                
                logger.info(f"🎉 Extracción completada:")
                logger.info(f"  📊 Total páginas procesadas: {page-1}/{total_pages or 'N/A'}")
                logger.info(f"  🏃‍♂️ Total jugadores guardados: {total_players_saved}")
                logger.info(f"  🏆 Liga: {league_id} | 📅 Temporada: {season}")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Error extrayendo jugadores: {e}")
            return False

    def extract_fixtures_by_league_season(self, league_id: int, season: int) -> bool:
        """
        Extrae fixtures (partidos) por liga y temporada
        Args:
            league_id: ID de la liga (ej: 39 para Premier League)
            season: Temporada (ej: 2018)
        """
        try:
            logger.info(f"⚽ Extrayendo fixtures de liga {league_id} temporada {season}")
            
            # Llamar a la API
            data = self.api_client.get_fixtures(league=league_id, season=season)
            
            if not data or 'response' not in data:
                logger.warning(f"❌ Sin datos de fixtures para liga {league_id} temporada {season}")
                return False
            
            fixtures_data = data['response']
            results_count = data.get('results', 0)
            
            logger.info(f"📊 {results_count} fixtures encontrados")
            
            if not fixtures_data:
                logger.info(f"✅ No hay fixtures para esta liga/temporada")
                return True
            
            fixtures_saved = 0
            fixtures_updated = 0
            
            with raw_db_manager.get_session() as session:
                for fixture_data in fixtures_data:
                    # Información básica del partido
                    fixture_info = fixture_data['fixture']
                    league_info = fixture_data['league']
                    teams_info = fixture_data['teams']
                    goals_info = fixture_data['goals']
                    score_info = fixture_data['score']
                    
                    # Procesar fecha
                    match_date = None
                    if fixture_info.get('date'):
                        from datetime import datetime
                        match_date = datetime.fromisoformat(fixture_info['date'].replace('Z', '+00:00'))
                    
                    # Crear registro de fixture
                    fixture_record = FootballMatchesRaw(
                        external_id=str(fixture_info['id']),
                        external_league_id=str(league_id),
                        season=str(season),
                        round=league_info.get('round'),
                        match_date=match_date,
                        timestamp_unix=fixture_info.get('timestamp'),
                        timezone=fixture_info.get('timezone'),
                        status_long=fixture_info.get('status', {}).get('long'),
                        status_short=fixture_info.get('status', {}).get('short'),
                        status_elapsed=fixture_info.get('status', {}).get('elapsed'),
                        venue_id=str(fixture_info.get('venue', {}).get('id')) if fixture_info.get('venue', {}).get('id') else None,
                        venue_name=fixture_info.get('venue', {}).get('name'),
                        venue_city=fixture_info.get('venue', {}).get('city'),
                        referee=fixture_info.get('referee'),
                        
                        # Equipos
                        home_team_external_id=str(teams_info['home']['id']),
                        home_team_name=teams_info['home']['name'],
                        home_team_logo=teams_info['home']['logo'],
                        away_team_external_id=str(teams_info['away']['id']),
                        away_team_name=teams_info['away']['name'],
                        away_team_logo=teams_info['away']['logo'],
                        
                        # Marcador
                        home_score=goals_info.get('home'),
                        away_score=goals_info.get('away'),
                        home_score_halftime=score_info.get('halftime', {}).get('home'),
                        away_score_halftime=score_info.get('halftime', {}).get('away'),
                        home_score_fulltime=score_info.get('fulltime', {}).get('home'),
                        away_score_fulltime=score_info.get('fulltime', {}).get('away'),
                        home_score_extratime=score_info.get('extratime', {}).get('home'),
                        away_score_extratime=score_info.get('extratime', {}).get('away'),
                        home_score_penalty=score_info.get('penalty', {}).get('home'),
                        away_score_penalty=score_info.get('penalty', {}).get('away'),
                        
                        # Metadatos
                        api_source='api-sports',
                        raw_json=fixture_data
                    )
                    
                    # Verificar si ya existe
                    existing_fixture = session.query(FootballMatchesRaw).filter_by(
                        external_id=str(fixture_info['id'])
                    ).first()
                    
                    if existing_fixture:
                        # Actualizar registro existente
                        for key, value in fixture_record.__dict__.items():
                            if not key.startswith('_'):
                                setattr(existing_fixture, key, value)
                        existing_fixture.updated_at = datetime.utcnow()
                        fixtures_updated += 1
                    else:
                        session.add(fixture_record)
                        fixtures_saved += 1
                
                session.commit()
                
                logger.info(f"🎉 Extracción de fixtures completada:")
                logger.info(f"  📊 Total fixtures procesados: {len(fixtures_data)}")
                logger.info(f"  📝 Nuevos: {fixtures_saved} | 🔄 Actualizados: {fixtures_updated}")
                logger.info(f"  🏆 Liga: {league_id} | 📅 Temporada: {season}")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Error extrayendo fixtures: {e}")
            return False

    def __del__(self):
        if hasattr(self, 'api_client'):
            self.api_client.close()