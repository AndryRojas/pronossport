import requests
from typing import Dict, List, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.config.settings import settings
from loguru import logger
import time

class APIClient:
    def __init__(self):
        self.base_url = settings.api_football_base_url
        self.api_key = settings.api_football_key
        self.host = settings.api_football_host
        self.timeout = settings.api_request_timeout
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        
        # Configurar reintentos automáticos
        retry_strategy = Retry(
            total=settings.retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers para API-Sports
        session.headers.update({
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': self.host,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        return session
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            logger.info(f"Realizando petición GET a: {url}")
            if params:
                logger.debug(f"Parámetros: {params}")
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Respuesta exitosa de {url}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición a {url}: {e}")
            return None
        except ValueError as e:
            logger.error(f"Error decodificando JSON de {url}: {e}")
            return None
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            logger.info(f"Realizando petición POST a: {url}")
            response = self.session.post(
                url,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Respuesta exitosa de {url}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición POST a {url}: {e}")
            return None
        except ValueError as e:
            logger.error(f"Error decodificando JSON de {url}: {e}")
            return None
    
    def get_paginated_data(self, endpoint: str, page_param: str = "page", 
                          start_page: int = 1, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        all_data = []
        current_page = start_page
        
        while True:
            if max_pages and current_page > max_pages:
                break
                
            params = {page_param: current_page}
            data = self.get(endpoint, params)
            
            if not data:
                break
            
            # Asumiendo que la respuesta tiene una estructura estándar
            # Esto se debe ajustar según la API específica
            if isinstance(data, list):
                if not data:
                    break
                all_data.extend(data)
            elif isinstance(data, dict):
                # Buscar datos en campos comunes
                items = data.get('data', data.get('results', data.get('items', [])))
                if not items:
                    break
                all_data.extend(items)
            
            current_page += 1
            time.sleep(0.5)  # Rate limiting
        
        logger.info(f"Obtenidos {len(all_data)} elementos de {endpoint}")
        return all_data
    
    def get_fixtures(self, date: Optional[str] = None, league: Optional[int] = None, 
                    season: Optional[int] = None, team: Optional[int] = None,
                    fixture_id: Optional[int] = None, date_from: Optional[str] = None, 
                    date_to: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene partidos de API-Sports
        Args:
            date: Fecha específica (YYYY-MM-DD)
            league: ID de la liga
            season: Temporada (YYYY)
            team: ID del equipo
            fixture_id: ID específico del partido
            date_from: Fecha inicio (YYYY-MM-DD)
            date_to: Fecha fin (YYYY-MM-DD)
        """
        params = {}
        
        if date:
            params['date'] = date
        if league:
            params['league'] = league
        if season:
            params['season'] = season
        if team:
            params['team'] = team
        if fixture_id:
            params['id'] = fixture_id
        if date_from:
            params['from'] = date_from
        if date_to:
            params['to'] = date_to
            
        return self.get('fixtures', params)
    
    def get_teams(self, league: Optional[int] = None, season: Optional[int] = None, 
                  team_id: Optional[int] = None, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene equipos de API-Sports
        Args:
            league: ID de la liga
            season: Temporada (YYYY)
            team_id: ID específico del equipo
            country: Código del país
        """
        params = {}
        
        if league:
            params['league'] = league
        if season:
            params['season'] = season
        if team_id:
            params['id'] = team_id
        if country:
            params['country'] = country
            
        return self.get('teams', params)
    
    def get_leagues(self, country: Optional[str] = None, league_id: Optional[int] = None,
                   season: Optional[int] = None, team: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene ligas de API-Sports
        Args:
            country: Código del país (ej: ES, EN, IT)
            league_id: ID específico de la liga
            season: Temporada (YYYY)
            team: ID del equipo
        """
        params = {}
        
        if country:
            params['country'] = country
        if league_id:
            params['id'] = league_id
        if season:
            params['season'] = season
        if team:
            params['team'] = team
            
        return self.get('leagues', params)
    
    def get_countries(self) -> Optional[Dict[str, Any]]:
        """Obtiene países disponibles en API-Sports"""
        return self.get('countries')
    
    def get_standings(self, league: int, season: int, team: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene tabla de posiciones de API-Sports
        Args:
            league: ID de la liga
            season: Temporada (YYYY)
            team: ID del equipo (opcional)
        """
        params = {
            'league': league,
            'season': season
        }
        
        if team:
            params['team'] = team
            
        return self.get('standings', params)
    
    def get_statistics(self, fixture: int, team: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene estadísticas de un partido
        Args:
            fixture: ID del partido
            team: ID del equipo
        """
        params = {
            'fixture': fixture,
            'team': team
        }
        return self.get('fixtures/statistics', params)
    
    def get_events(self, fixture: int, team: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene eventos de un partido
        Args:
            fixture: ID del partido
            team: ID del equipo (opcional)
        """
        params = {
            'fixture': fixture
        }
        
        if team:
            params['team'] = team
            
        return self.get('fixtures/events', params)
    
    def get_lineups(self, fixture: int, team: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene alineaciones de un partido
        Args:
            fixture: ID del partido
            team: ID del equipo (opcional)
        """
        params = {
            'fixture': fixture
        }
        
        if team:
            params['team'] = team
            
        return self.get('fixtures/lineups', params)
    
    def get_players_statistics(self, fixture: int, team: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene estadísticas de jugadores de un partido
        Args:
            fixture: ID del partido
            team: ID del equipo (opcional)
        """
        params = {
            'fixture': fixture
        }
        
        if team:
            params['team'] = team
            
        return self.get('fixtures/players', params)
    
    def get_odds(self, fixture: int, bet: Optional[int] = None, bookmaker: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene cuotas de apuestas
        Args:
            fixture: ID del partido
            bet: ID del tipo de apuesta
            bookmaker: ID del bookmaker
        """
        params = {
            'fixture': fixture
        }
        
        if bet:
            params['bet'] = bet
        if bookmaker:
            params['bookmaker'] = bookmaker
            
        return self.get('odds', params)
    
    def get_players(self, league: int, season: int, team: Optional[int] = None, 
                   player_id: Optional[int] = None, page: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene jugadores con estadísticas por liga y temporada
        Args:
            league: ID de la liga (requerido)
            season: Temporada (requerido) 
            team: ID del equipo (opcional)
            player_id: ID específico del jugador (opcional)
            page: Página para paginación (opcional)
        """
        params = {
            'league': league,
            'season': season
        }
        
        if team:
            params['team'] = team
        if player_id:
            params['id'] = player_id
        if page:
            params['page'] = page
            
        return self.get('players', params)

    def close(self):
        self.session.close()