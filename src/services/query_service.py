from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from src.database.connection import raw_db_manager
from src.models.raw_models import LeaguesRaw
from loguru import logger

class RawQueryService:
    """
    Servicio para consultas a la base de datos raw_pronossport.
    Proporciona métodos para consultar información de las diferentes tablas.
    """
    
    def __init__(self):
        self.db_manager = raw_db_manager
    
    def _paginate_query(self, query, page: int = 1, per_page: int = 50) -> Tuple[List, Dict[str, Any]]:
        """
        Aplica paginación a una consulta SQLAlchemy.
        
        Args:
            query: Consulta SQLAlchemy
            page: Página actual (empezando en 1)
            per_page: Registros por página
            
        Returns:
            Tuple: (resultados, información_paginación)
        """
        # Calcular offset
        offset = (page - 1) * per_page
        
        # Obtener total de registros
        total = query.count()
        
        # Aplicar paginación
        results = query.offset(offset).limit(per_page).all()
        
        # Calcular información de paginación
        total_pages = (total + per_page - 1) // per_page  # Redondear hacia arriba
        has_prev = page > 1
        has_next = page < total_pages
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': page - 1 if has_prev else None,
            'next_num': page + 1 if has_next else None
        }
        
        return results, pagination_info
    
    def get_leagues_by_country_and_season(self, season: Optional[str] = None, country: Optional[str] = None, 
                                        page: int = 1, per_page: int = 50) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Obtiene todas las ligas agrupadas por país y liga, filtradas por temporada y país con paginación.
        
        Args:
            season (str, optional): Temporada a filtrar (ej: '2023', '2024')
            country (str, optional): País a filtrar
            page (int): Página actual (empezando en 1)
            per_page (int): Registros por página
            
        Returns:
            Tuple: (Lista de diccionarios con información de ligas, información de paginación)
        """
        try:
            with self.db_manager.get_session() as session:
                query = session.query(
                    LeaguesRaw.country,
                    LeaguesRaw.country_code,
                    LeaguesRaw.name.label('league_name'),
                    LeaguesRaw.external_id,
                    LeaguesRaw.season,
                    LeaguesRaw.season_start,
                    LeaguesRaw.season_end,
                    LeaguesRaw.logo_url,
                    LeaguesRaw.flag_url,
                    func.count(LeaguesRaw.id).label('total_records')
                ).group_by(
                    LeaguesRaw.country,
                    LeaguesRaw.country_code,
                    LeaguesRaw.name,
                    LeaguesRaw.external_id,
                    LeaguesRaw.season,
                    LeaguesRaw.season_start,
                    LeaguesRaw.season_end,
                    LeaguesRaw.logo_url,
                    LeaguesRaw.flag_url
                )
                
                # Aplicar filtros si se proporcionan
                if season:
                    query = query.filter(LeaguesRaw.season == season)
                if country:
                    query = query.filter(LeaguesRaw.country == country)
                
                # Ordenar por país y luego por nombre de liga
                query = query.order_by(
                    LeaguesRaw.country.asc(),
                    LeaguesRaw.name.asc()
                )
                
                # Aplicar paginación
                results, pagination_info = self._paginate_query(query, page, per_page)
                
                # Convertir a lista de diccionarios
                leagues_data = []
                for result in results:
                    leagues_data.append({
                        'country': result.country,
                        'country_code': result.country_code,
                        'league_name': result.league_name,
                        'external_id': result.external_id,
                        'season': result.season,
                        'season_start': result.season_start.isoformat() if result.season_start else None,
                        'season_end': result.season_end.isoformat() if result.season_end else None,
                        'logo_url': result.logo_url,
                        'flag_url': result.flag_url,
                        'total_records': result.total_records
                    })
                
                logger.info(f"Consulta de ligas completada. Página {page}, {len(leagues_data)} ligas de {pagination_info['total']} totales")
                return leagues_data, pagination_info
                
        except Exception as e:
            logger.error(f"Error al consultar ligas por país y temporada: {e}")
            raise
    
    def get_leagues_summary_by_country(self, season: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen de ligas agrupadas por país.
        
        Args:
            season (str, optional): Temporada a filtrar
            
        Returns:
            List[Dict]: Lista con resumen por país
        """
        try:
            with self.db_manager.get_session() as session:
                query = session.query(
                    LeaguesRaw.country,
                    LeaguesRaw.country_code,
                    func.count(func.distinct(LeaguesRaw.name)).label('total_leagues'),
                    func.count(LeaguesRaw.id).label('total_records')
                ).group_by(
                    LeaguesRaw.country,
                    LeaguesRaw.country_code
                )
                
                if season:
                    query = query.filter(LeaguesRaw.season == season)
                
                query = query.order_by(LeaguesRaw.country.asc())
                
                results = query.all()
                
                summary_data = []
                for result in results:
                    summary_data.append({
                        'country': result.country,
                        'country_code': result.country_code,
                        'total_leagues': result.total_leagues,
                        'total_records': result.total_records
                    })
                
                logger.info(f"Resumen por país completado. Total: {len(summary_data)} países encontrados")
                return summary_data
                
        except Exception as e:
            logger.error(f"Error al obtener resumen por país: {e}")
            raise
    
    def get_available_seasons(self) -> List[str]:
        """
        Obtiene todas las temporadas disponibles en la tabla leagues_raw.
        
        Returns:
            List[str]: Lista de temporadas disponibles
        """
        try:
            with self.db_manager.get_session() as session:
                seasons = session.query(
                    func.distinct(LeaguesRaw.season)
                ).filter(
                    LeaguesRaw.season.isnot(None)
                ).order_by(
                    LeaguesRaw.season.desc()
                ).all()
                
                season_list = [season[0] for season in seasons if season[0]]
                
                logger.info(f"Temporadas disponibles obtenidas: {season_list}")
                return season_list
                
        except Exception as e:
            logger.error(f"Error al obtener temporadas disponibles: {e}")
            raise
    
    def get_leagues_by_country(self, country: str, season: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene todas las ligas de un país específico.
        
        Args:
            country (str): Nombre del país
            season (str, optional): Temporada a filtrar
            
        Returns:
            List[Dict]: Lista de ligas del país especificado
        """
        try:
            with self.db_manager.get_session() as session:
                query = session.query(LeaguesRaw).filter(
                    LeaguesRaw.country == country
                )
                
                if season:
                    query = query.filter(LeaguesRaw.season == season)
                
                query = query.order_by(LeaguesRaw.name.asc())
                
                results = query.all()
                
                leagues_data = []
                for league in results:
                    leagues_data.append({
                        'id': league.id,
                        'external_id': league.external_id,
                        'name': league.name,
                        'country': league.country,
                        'country_code': league.country_code,
                        'season': league.season,
                        'season_start': league.season_start.isoformat() if league.season_start else None,
                        'season_end': league.season_end.isoformat() if league.season_end else None,
                        'logo_url': league.logo_url,
                        'flag_url': league.flag_url,
                        'api_source': league.api_source,
                        'created_at': league.created_at.isoformat() if league.created_at else None,
                        'updated_at': league.updated_at.isoformat() if league.updated_at else None
                    })
                
                logger.info(f"Ligas del país {country} obtenidas: {len(leagues_data)} ligas")
                return leagues_data
                
        except Exception as e:
            logger.error(f"Error al obtener ligas del país {country}: {e}")
            raise
    
    def get_league_details(self, external_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de una liga específica por su external_id.
        
        Args:
            external_id (str): ID externo de la liga
            
        Returns:
            Dict: Detalles de la liga o None si no se encuentra
        """
        try:
            with self.db_manager.get_session() as session:
                league = session.query(LeaguesRaw).filter(
                    LeaguesRaw.external_id == external_id
                ).first()
                
                if league:
                    league_data = {
                        'id': league.id,
                        'external_id': league.external_id,
                        'name': league.name,
                        'country': league.country,
                        'country_code': league.country_code,
                        'season': league.season,
                        'season_start': league.season_start.isoformat() if league.season_start else None,
                        'season_end': league.season_end.isoformat() if league.season_end else None,
                        'logo_url': league.logo_url,
                        'flag_url': league.flag_url,
                        'api_source': league.api_source,
                        'raw_json': league.raw_json,
                        'created_at': league.created_at.isoformat() if league.created_at else None,
                        'updated_at': league.updated_at.isoformat() if league.updated_at else None
                    }
                    
                    logger.info(f"Detalles de liga obtenidos para external_id: {external_id}")
                    return league_data
                else:
                    logger.warning(f"No se encontró liga con external_id: {external_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error al obtener detalles de liga {external_id}: {e}")
            raise