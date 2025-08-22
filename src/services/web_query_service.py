from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from src.database.connection import raw_db_manager
from src.models.raw_models import (
    LeaguesRaw, TeamsRaw, PlayersRaw, FootballMatchesRaw,
    FootballPlayerSeasonStatsRaw, FootballPlayerMatchStatsRaw,
    FootballMatchStatisticsRaw, FootballStandingsRaw
)
from loguru import logger

class WebQueryService:
    """
    Servicio especializado para consultas de la interfaz web.
    Proporciona métodos optimizados para el dashboard y visualizaciones.
    """
    
    def __init__(self):
        self.db_manager = raw_db_manager
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales para el dashboard principal.
        
        Returns:
            Dict: Estadísticas generales del sistema
        """
        try:
            with self.db_manager.get_session() as session:
                # Contar totales
                total_leagues = session.query(func.count(func.distinct(LeaguesRaw.external_id))).scalar() or 0
                total_countries = session.query(func.count(func.distinct(LeaguesRaw.country))).scalar() or 0
                total_teams = session.query(func.count(func.distinct(TeamsRaw.external_id))).scalar() or 0
                total_players = session.query(func.count(func.distinct(PlayersRaw.external_id))).scalar() or 0
                total_matches = session.query(func.count(func.distinct(FootballMatchesRaw.external_id))).scalar() or 0
                
                # Obtener temporadas disponibles
                seasons = session.query(func.distinct(LeaguesRaw.season)).filter(
                    LeaguesRaw.season.isnot(None)
                ).count()
                
                # Países con más ligas (top 5)
                top_countries = session.query(
                    LeaguesRaw.country,
                    func.count(func.distinct(LeaguesRaw.external_id)).label('league_count')
                ).group_by(LeaguesRaw.country).order_by(
                    desc('league_count')
                ).limit(5).all()
                
                # Ligas con más equipos (top 5)
                top_leagues = session.query(
                    LeaguesRaw.name,
                    LeaguesRaw.country,
                    func.count(func.distinct(TeamsRaw.external_id)).label('team_count')
                ).join(
                    TeamsRaw, 
                    LeaguesRaw.external_id == TeamsRaw.extracted_for_league,
                    isouter=True
                ).group_by(
                    LeaguesRaw.name, 
                    LeaguesRaw.country
                ).order_by(
                    desc('team_count')
                ).limit(5).all()
                
                stats = {
                    'totals': {
                        'leagues': total_leagues,
                        'countries': total_countries,
                        'teams': total_teams,
                        'players': total_players,
                        'matches': total_matches,
                        'seasons': seasons
                    },
                    'top_countries': [
                        {'country': country, 'leagues': count} 
                        for country, count in top_countries
                    ],
                    'top_leagues': [
                        {'name': name, 'country': country, 'teams': count}
                        for name, country, count in top_leagues
                    ]
                }
                
                logger.info("Estadísticas del dashboard obtenidas exitosamente")
                return stats
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del dashboard: {e}")
            raise
    
    def get_available_countries(self) -> List[str]:
        """
        Obtiene lista de países disponibles.
        
        Returns:
            List[str]: Lista de países
        """
        try:
            with self.db_manager.get_session() as session:
                countries = session.query(
                    func.distinct(LeaguesRaw.country)
                ).filter(
                    LeaguesRaw.country.isnot(None)
                ).order_by(
                    LeaguesRaw.country.asc()
                ).all()
                
                return [country[0] for country in countries if country[0]]
                
        except Exception as e:
            logger.error(f"Error obteniendo países disponibles: {e}")
            raise
    
    def get_leagues_for_filter(self) -> List[Dict[str, Any]]:
        """
        Obtiene ligas para usar en filtros de selección.
        
        Returns:
            List[Dict]: Lista de ligas con información básica
        """
        try:
            with self.db_manager.get_session() as session:
                leagues = session.query(
                    func.distinct(LeaguesRaw.external_id).label('external_id'),
                    LeaguesRaw.name,
                    LeaguesRaw.country,
                    LeaguesRaw.season
                ).order_by(
                    LeaguesRaw.country.asc(),
                    LeaguesRaw.name.asc()
                ).all()
                
                leagues_data = []
                for league in leagues:
                    leagues_data.append({
                        'external_id': league.external_id,
                        'name': league.name,
                        'country': league.country,
                        'season': league.season,
                        'display_name': f"{league.name} ({league.country}) - {league.season}"
                    })
                
                return leagues_data
                
        except Exception as e:
            logger.error(f"Error obteniendo ligas para filtro: {e}")
            raise
    
    def get_teams_for_filter(self) -> List[Dict[str, Any]]:
        """
        Obtiene equipos para usar en filtros de selección.
        
        Returns:
            List[Dict]: Lista de equipos con información básica
        """
        try:
            with self.db_manager.get_session() as session:
                teams = session.query(
                    func.distinct(TeamsRaw.external_id).label('external_id'),
                    TeamsRaw.name,
                    TeamsRaw.country
                ).order_by(
                    TeamsRaw.country.asc(),
                    TeamsRaw.name.asc()
                ).limit(1000).all()  # Limitar para performance
                
                teams_data = []
                for team in teams:
                    teams_data.append({
                        'external_id': team.external_id,
                        'name': team.name,
                        'country': team.country,
                        'display_name': f"{team.name} ({team.country})"
                    })
                
                return teams_data
                
        except Exception as e:
            logger.error(f"Error obteniendo equipos para filtro: {e}")
            raise
    
    def get_teams_summary(self, league_id: Optional[str] = None, 
                         season: Optional[str] = None,
                         country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene resumen de equipos con filtros opcionales.
        
        Args:
            league_id: ID de liga para filtrar
            season: Temporada para filtrar
            country: País para filtrar
            
        Returns:
            List[Dict]: Lista de equipos con estadísticas
        """
        try:
            with self.db_manager.get_session() as session:
                query = session.query(
                    TeamsRaw.external_id,
                    TeamsRaw.name,
                    TeamsRaw.country,
                    TeamsRaw.extracted_for_league,
                    TeamsRaw.extracted_for_season,
                    TeamsRaw.logo_url,
                    TeamsRaw.venue_name,
                    TeamsRaw.venue_city,
                    func.count(PlayersRaw.id).label('players_count')
                ).outerjoin(
                    PlayersRaw,
                    TeamsRaw.external_id == PlayersRaw.external_team_id
                ).group_by(
                    TeamsRaw.external_id,
                    TeamsRaw.name,
                    TeamsRaw.country,
                    TeamsRaw.extracted_for_league,
                    TeamsRaw.extracted_for_season,
                    TeamsRaw.logo_url,
                    TeamsRaw.venue_name,
                    TeamsRaw.venue_city
                )
                
                # Aplicar filtros
                if league_id:
                    query = query.filter(TeamsRaw.extracted_for_league == league_id)
                
                if season:
                    query = query.filter(TeamsRaw.extracted_for_season == season)
                
                if country:
                    query = query.filter(TeamsRaw.country == country)
                
                query = query.order_by(TeamsRaw.country.asc(), TeamsRaw.name.asc())
                
                results = query.all()
                
                teams_data = []
                for team in results:
                    teams_data.append({
                        'external_id': team.external_id,
                        'name': team.name,
                        'country': team.country,
                        'league_id': team.extracted_for_league,
                        'season': team.extracted_for_season,
                        'logo_url': team.logo_url,
                        'venue_name': team.venue_name,
                        'venue_city': team.venue_city,
                        'players_count': team.players_count or 0
                    })
                
                logger.info(f"Resumen de equipos obtenido: {len(teams_data)} equipos")
                return teams_data
                
        except Exception as e:
            logger.error(f"Error obteniendo resumen de equipos: {e}")
            raise
    
    def get_players_summary(self, team_id: Optional[str] = None,
                           league_id: Optional[str] = None,
                           season: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene resumen de jugadores con filtros opcionales.
        
        Args:
            team_id: ID de equipo para filtrar
            league_id: ID de liga para filtrar
            season: Temporada para filtrar
            
        Returns:
            List[Dict]: Lista de jugadores con estadísticas
        """
        try:
            with self.db_manager.get_session() as session:
                query = session.query(
                    PlayersRaw.external_id,
                    PlayersRaw.name,
                    PlayersRaw.firstname,
                    PlayersRaw.lastname,
                    PlayersRaw.external_team_id,
                    PlayersRaw.external_league_id,
                    PlayersRaw.season,
                    PlayersRaw.nationality,
                    PlayersRaw.position,
                    PlayersRaw.birth_date,
                    PlayersRaw.photo_url,
                    PlayersRaw.height,
                    PlayersRaw.weight,
                    PlayersRaw.number,
                    TeamsRaw.name.label('team_name')
                ).outerjoin(
                    TeamsRaw,
                    PlayersRaw.external_team_id == TeamsRaw.external_id
                )
                
                # Aplicar filtros
                if team_id:
                    query = query.filter(PlayersRaw.external_team_id == team_id)
                
                if league_id:
                    query = query.filter(PlayersRaw.external_league_id == league_id)
                
                if season:
                    query = query.filter(PlayersRaw.season == season)
                
                query = query.order_by(
                    TeamsRaw.name.asc(),
                    PlayersRaw.name.asc()
                )
                
                results = query.limit(1000).all()  # Limitar para performance
                
                players_data = []
                for player in results:
                    players_data.append({
                        'external_id': player.external_id,
                        'name': player.name,
                        'firstname': player.firstname,
                        'lastname': player.lastname,
                        'team_id': player.external_team_id,
                        'team_name': player.team_name,
                        'league_id': player.external_league_id,
                        'season': player.season,
                        'nationality': player.nationality,
                        'position': player.position,
                        'birth_date': player.birth_date.isoformat() if player.birth_date else None,
                        'photo_url': player.photo_url,
                        'height': player.height,
                        'weight': player.weight,
                        'number': player.number
                    })
                
                logger.info(f"Resumen de jugadores obtenido: {len(players_data)} jugadores")
                return players_data
                
        except Exception as e:
            logger.error(f"Error obteniendo resumen de jugadores: {e}")
            raise
    
    def get_matches_summary(self, league_id: Optional[str] = None,
                           season: Optional[str] = None,
                           date_from: Optional[str] = None,
                           date_to: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene resumen de partidos con filtros opcionales.
        
        Args:
            league_id: ID de liga para filtrar
            season: Temporada para filtrar
            date_from: Fecha desde (YYYY-MM-DD)
            date_to: Fecha hasta (YYYY-MM-DD)
            
        Returns:
            List[Dict]: Lista de partidos con información básica
        """
        try:
            with self.db_manager.get_session() as session:
                query = session.query(
                    FootballMatchesRaw.external_id,
                    FootballMatchesRaw.external_league_id,
                    FootballMatchesRaw.season,
                    FootballMatchesRaw.match_date,
                    FootballMatchesRaw.round,
                    FootballMatchesRaw.status_short,
                    FootballMatchesRaw.home_team_name,
                    FootballMatchesRaw.away_team_name,
                    FootballMatchesRaw.home_score,
                    FootballMatchesRaw.away_score,
                    FootballMatchesRaw.venue_name,
                    FootballMatchesRaw.venue_city
                )
                
                # Aplicar filtros
                if league_id:
                    query = query.filter(FootballMatchesRaw.external_league_id == league_id)
                
                if season:
                    query = query.filter(FootballMatchesRaw.season == season)
                
                if date_from:
                    query = query.filter(FootballMatchesRaw.match_date >= date_from)
                
                if date_to:
                    query = query.filter(FootballMatchesRaw.match_date <= date_to)
                
                query = query.order_by(FootballMatchesRaw.match_date.desc())
                
                results = query.limit(1000).all()  # Limitar para performance
                
                matches_data = []
                for match in results:
                    matches_data.append({
                        'external_id': match.external_id,
                        'league_id': match.external_league_id,
                        'season': match.season,
                        'match_date': match.match_date.isoformat() if match.match_date else None,
                        'round': match.round,
                        'status': match.status_short,
                        'home_team': match.home_team_name,
                        'away_team': match.away_team_name,
                        'home_score': match.home_score,
                        'away_score': match.away_score,
                        'venue_name': match.venue_name,
                        'venue_city': match.venue_city
                    })
                
                logger.info(f"Resumen de partidos obtenido: {len(matches_data)} partidos")
                return matches_data
                
        except Exception as e:
            logger.error(f"Error obteniendo resumen de partidos: {e}")
            raise
    
    def get_administration_leagues_data(self, filter_type: str = 'all', country: Optional[str] = None, 
                                       league_name: Optional[str] = None, season: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene datos de administración de ligas con conteos de equipos y partidos.
        
        Args:
            filter_type: 'all' para todos, 'no_data' para sin datos en partidos
            country: País para filtrar
            league_name: Nombre de liga para filtrar
            season: Temporada para filtrar
            
        Returns:
            List[Dict]: Lista con información de administración de ligas
        """
        try:
            with self.db_manager.get_session() as session:
                # Subconsulta para contar equipos por liga
                teams_subquery = session.query(
                    TeamsRaw.extracted_for_league.label('league_id'),
                    func.count(func.distinct(TeamsRaw.external_id)).label('teams_count')
                ).group_by(TeamsRaw.extracted_for_league).subquery()
                
                # Subconsulta para contar partidos por liga
                matches_subquery = session.query(
                    FootballMatchesRaw.external_league_id.label('league_id'),
                    func.count(func.distinct(FootballMatchesRaw.external_id)).label('matches_count')
                ).group_by(FootballMatchesRaw.external_league_id).subquery()
                
                # Consulta principal
                query = session.query(
                    LeaguesRaw.external_id,
                    LeaguesRaw.name,
                    LeaguesRaw.country,
                    LeaguesRaw.season,
                    LeaguesRaw.logo_url,
                    func.coalesce(teams_subquery.c.teams_count, 0).label('teams_count'),
                    func.coalesce(matches_subquery.c.matches_count, 0).label('matches_count')
                ).outerjoin(
                    teams_subquery,
                    LeaguesRaw.external_id == teams_subquery.c.league_id
                ).outerjoin(
                    matches_subquery,
                    LeaguesRaw.external_id == matches_subquery.c.league_id
                ).group_by(
                    LeaguesRaw.external_id,
                    LeaguesRaw.name,
                    LeaguesRaw.country,
                    LeaguesRaw.season,
                    LeaguesRaw.logo_url,
                    teams_subquery.c.teams_count,
                    matches_subquery.c.matches_count
                )
                
                # Aplicar filtros básicos
                if country:
                    query = query.filter(LeaguesRaw.country == country)
                
                if league_name:
                    query = query.filter(LeaguesRaw.name == league_name)
                
                if season:
                    query = query.filter(LeaguesRaw.season == season)
                
                # Aplicar filtro de datos
                if filter_type == 'no_data':
                    query = query.having(func.coalesce(matches_subquery.c.matches_count, 0) == 0)
                
                query = query.order_by(
                    LeaguesRaw.country.asc(),
                    LeaguesRaw.name.asc()
                )
                
                results = query.all()
                
                leagues_data = []
                for result in results:
                    leagues_data.append({
                        'external_id': result.external_id,
                        'name': result.name,
                        'country': result.country,
                        'season': result.season,
                        'logo_url': result.logo_url,
                        'teams_count': result.teams_count or 0,
                        'matches_count': result.matches_count or 0,
                        'has_matches': (result.matches_count or 0) > 0
                    })
                
                logger.info(f"Datos de administración de ligas obtenidos: {len(leagues_data)} ligas")
                return leagues_data
                
        except Exception as e:
            logger.error(f"Error obteniendo datos de administración de ligas: {e}")
            raise
    
    def get_administration_teams_data(self, league_id: str, filter_type: str = 'all') -> List[Dict[str, Any]]:
        """
        Obtiene datos de administración de equipos para una liga específica.
        
        Args:
            league_id: ID de la liga
            filter_type: 'all' para todos, 'no_data' para sin datos en jugadores
            
        Returns:
            List[Dict]: Lista con información de administración de equipos
        """
        try:
            with self.db_manager.get_session() as session:
                # Subconsulta para contar jugadores por equipo
                players_subquery = session.query(
                    PlayersRaw.external_team_id.label('team_id'),
                    func.count(func.distinct(PlayersRaw.external_id)).label('players_count')
                ).group_by(PlayersRaw.external_team_id).subquery()
                
                # Consulta principal
                query = session.query(
                    TeamsRaw.external_id,
                    TeamsRaw.name,
                    TeamsRaw.country,
                    TeamsRaw.logo_url,
                    TeamsRaw.venue_name,
                    func.coalesce(players_subquery.c.players_count, 0).label('players_count')
                ).outerjoin(
                    players_subquery,
                    TeamsRaw.external_id == players_subquery.c.team_id
                ).filter(
                    TeamsRaw.extracted_for_league == league_id
                ).group_by(
                    TeamsRaw.external_id,
                    TeamsRaw.name,
                    TeamsRaw.country,
                    TeamsRaw.logo_url,
                    TeamsRaw.venue_name,
                    players_subquery.c.players_count
                )
                
                # Aplicar filtro si es necesario
                if filter_type == 'no_data':
                    query = query.having(func.coalesce(players_subquery.c.players_count, 0) == 0)
                
                query = query.order_by(TeamsRaw.name.asc())
                
                results = query.all()
                
                teams_data = []
                for result in results:
                    teams_data.append({
                        'external_id': result.external_id,
                        'name': result.name,
                        'country': result.country,
                        'logo_url': result.logo_url,
                        'venue_name': result.venue_name,
                        'players_count': result.players_count or 0,
                        'has_players': (result.players_count or 0) > 0
                    })
                
                logger.info(f"Datos de administración de equipos obtenidos: {len(teams_data)} equipos para liga {league_id}")
                return teams_data
                
        except Exception as e:
            logger.error(f"Error obteniendo datos de administración de equipos: {e}")
            raise
    
    def get_league_details_for_admin(self, league_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles de una liga para la sección de administración.
        
        Args:
            league_id: ID de la liga
            
        Returns:
            Dict: Detalles de la liga o None si no se encuentra
        """
        try:
            with self.db_manager.get_session() as session:
                league = session.query(LeaguesRaw).filter(
                    LeaguesRaw.external_id == league_id
                ).first()
                
                if league:
                    return {
                        'external_id': league.external_id,
                        'name': league.name,
                        'country': league.country,
                        'season': league.season,
                        'logo_url': league.logo_url,
                        'flag_url': league.flag_url
                    }
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error obteniendo detalles de liga para admin: {e}")
            raise
    
    def get_administration_countries(self) -> List[str]:
        """
        Obtiene lista de países disponibles para administración.
        
        Returns:
            List[str]: Lista de países
        """
        try:
            with self.db_manager.get_session() as session:
                countries = session.query(
                    func.distinct(LeaguesRaw.country)
                ).filter(
                    LeaguesRaw.country.isnot(None)
                ).order_by(
                    LeaguesRaw.country.asc()
                ).all()
                
                return [country[0] for country in countries if country[0]]
                
        except Exception as e:
            logger.error(f"Error obteniendo países para administración: {e}")
            raise
    
    def get_administration_leagues_by_country(self, country: str) -> List[Dict[str, str]]:
        """
        Obtiene ligas disponibles para un país específico en administración.
        
        Args:
            country: País para filtrar
            
        Returns:
            List[Dict]: Lista de ligas con nombre y external_id
        """
        try:
            with self.db_manager.get_session() as session:
                leagues = session.query(
                    LeaguesRaw.name,
                    LeaguesRaw.external_id
                ).filter(
                    LeaguesRaw.country == country
                ).group_by(
                    LeaguesRaw.name,
                    LeaguesRaw.external_id
                ).order_by(
                    LeaguesRaw.name.asc()
                ).all()
                
                leagues_data = []
                seen_names = set()
                for league in leagues:
                    if league.name not in seen_names:
                        leagues_data.append({
                            'name': league.name,
                            'external_id': league.external_id
                        })
                        seen_names.add(league.name)
                
                return leagues_data
                
        except Exception as e:
            logger.error(f"Error obteniendo ligas por país para administración: {e}")
            raise
    
    def get_administration_seasons_by_league(self, league_name: str, country: str) -> List[str]:
        """
        Obtiene temporadas disponibles para una liga específica en administración.
        
        Args:
            league_name: Nombre de la liga
            country: País de la liga
            
        Returns:
            List[str]: Lista de temporadas
        """
        try:
            with self.db_manager.get_session() as session:
                seasons = session.query(
                    func.distinct(LeaguesRaw.season)
                ).filter(
                    and_(
                        LeaguesRaw.name == league_name,
                        LeaguesRaw.country == country,
                        LeaguesRaw.season.isnot(None)
                    )
                ).order_by(
                    LeaguesRaw.season.desc()
                ).all()
                
                return [season[0] for season in seasons if season[0]]
                
        except Exception as e:
            logger.error(f"Error obteniendo temporadas por liga para administración: {e}")
            raise