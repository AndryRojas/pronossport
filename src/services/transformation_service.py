from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.database.connection import raw_db_manager, pronos_db_manager
from src.models.raw_models import RawMatchData, RawTeamData
from src.models.pronos_models import Team, Match, MatchStatistic, ProcessingLog
from src.config.settings import settings
from loguru import logger
import json

class TransformationService:
    
    def transform_teams(self, batch_size: Optional[int] = None) -> int:
        if not batch_size:
            batch_size = settings.batch_size
        
        processed_count = 0
        
        try:
            with raw_db_manager.get_session() as raw_session:
                # Obtener equipos no procesados
                raw_teams = (raw_session.query(RawTeamData)
                           .filter(RawTeamData.processed == 0)
                           .limit(batch_size)
                           .all())
                
                if not raw_teams:
                    logger.info("No hay equipos pendientes de procesar")
                    return 0
                
                with pronos_db_manager.get_session() as pronos_session:
                    for raw_team in raw_teams:
                        try:
                            team_data = raw_team.raw_json
                            
                            # Transformar datos del equipo
                            transformed_team = self._transform_team_data(team_data)
                            
                            if transformed_team:
                                # Verificar si ya existe en la base de datos transformada
                                existing_team = (pronos_session.query(Team)
                                               .filter(Team.external_id == raw_team.external_id)
                                               .first())
                                
                                if existing_team:
                                    # Actualizar equipo existente
                                    self._update_team(existing_team, transformed_team)
                                    processed_record_id = existing_team.id
                                else:
                                    # Crear nuevo equipo
                                    new_team = Team(**transformed_team)
                                    pronos_session.add(new_team)
                                    pronos_session.flush()
                                    processed_record_id = new_team.id
                                
                                # Marcar como procesado en raw
                                raw_team.processed = 1
                                
                                # Crear log de procesamiento
                                processing_log = ProcessingLog(
                                    raw_table='raw_teams',
                                    raw_record_id=raw_team.id,
                                    processed_table='teams',
                                    processed_record_id=processed_record_id,
                                    processing_status='success'
                                )
                                pronos_session.add(processing_log)
                                processed_count += 1
                            
                        except Exception as e:
                            logger.error(f"Error procesando equipo {raw_team.id}: {e}")
                            raw_team.processed = -1  # Marcar como error
                            
                            processing_log = ProcessingLog(
                                raw_table='raw_teams',
                                raw_record_id=raw_team.id,
                                processing_status='error',
                                error_message=str(e)
                            )
                            pronos_session.add(processing_log)
                
                logger.info(f"Procesados {processed_count} equipos")
                return processed_count
                
        except Exception as e:
            logger.error(f"Error en transformación de equipos: {e}")
            return 0
    
    def transform_matches(self, batch_size: Optional[int] = None) -> int:
        if not batch_size:
            batch_size = settings.batch_size
        
        processed_count = 0
        
        try:
            with raw_db_manager.get_session() as raw_session:
                # Obtener partidos no procesados
                raw_matches = (raw_session.query(RawMatchData)
                             .filter(RawMatchData.processed == 0)
                             .limit(batch_size)
                             .all())
                
                if not raw_matches:
                    logger.info("No hay partidos pendientes de procesar")
                    return 0
                
                with pronos_db_manager.get_session() as pronos_session:
                    for raw_match in raw_matches:
                        try:
                            match_data = raw_match.raw_json
                            
                            # Transformar datos del partido
                            transformed_match = self._transform_match_data(match_data, pronos_session)
                            
                            if transformed_match:
                                # Verificar si ya existe en la base de datos transformada
                                existing_match = (pronos_session.query(Match)
                                                .filter(Match.external_id == raw_match.external_id)
                                                .first())
                                
                                if existing_match:
                                    # Actualizar partido existente
                                    self._update_match(existing_match, transformed_match)
                                    processed_record_id = existing_match.id
                                else:
                                    # Crear nuevo partido
                                    new_match = Match(**transformed_match)
                                    pronos_session.add(new_match)
                                    pronos_session.flush()
                                    processed_record_id = new_match.id
                                    
                                    # Procesar estadísticas si existen
                                    if 'statistics' in match_data:
                                        self._process_match_statistics(match_data['statistics'], 
                                                                     processed_record_id, pronos_session)
                                
                                # Marcar como procesado en raw
                                raw_match.processed = 1
                                
                                # Crear log de procesamiento
                                processing_log = ProcessingLog(
                                    raw_table='raw_matches',
                                    raw_record_id=raw_match.id,
                                    processed_table='matches',
                                    processed_record_id=processed_record_id,
                                    processing_status='success'
                                )
                                pronos_session.add(processing_log)
                                processed_count += 1
                            
                        except Exception as e:
                            logger.error(f"Error procesando partido {raw_match.id}: {e}")
                            raw_match.processed = -1  # Marcar como error
                            
                            processing_log = ProcessingLog(
                                raw_table='raw_matches',
                                raw_record_id=raw_match.id,
                                processing_status='error',
                                error_message=str(e)
                            )
                            pronos_session.add(processing_log)
                
                logger.info(f"Procesados {processed_count} partidos")
                return processed_count
                
        except Exception as e:
            logger.error(f"Error en transformación de partidos: {e}")
            return 0
    
    def _transform_team_data(self, team_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            return {
                'external_id': str(team_data.get('id', team_data.get('team_id'))),
                'name': team_data.get('name', team_data.get('team_name', '')),
                'short_name': team_data.get('short_name', team_data.get('abbreviation', ''))[:10],
                'country': team_data.get('country', team_data.get('nationality', '')),
                'league': team_data.get('league', team_data.get('competition', '')),
                'logo_url': team_data.get('logo', team_data.get('logo_url', ''))
            }
        except Exception as e:
            logger.error(f"Error transformando datos de equipo: {e}")
            return None
    
    def _transform_match_data(self, match_data: Dict[str, Any], session: Session) -> Optional[Dict[str, Any]]:
        try:
            # Obtener o buscar equipos
            home_team_external_id = str(match_data.get('home_team', {}).get('id', 
                                                       match_data.get('home_team_id', '')))
            away_team_external_id = str(match_data.get('away_team', {}).get('id', 
                                                       match_data.get('away_team_id', '')))
            
            home_team = session.query(Team).filter(Team.external_id == home_team_external_id).first()
            away_team = session.query(Team).filter(Team.external_id == away_team_external_id).first()
            
            if not home_team or not away_team:
                logger.warning(f"Equipos no encontrados: home={home_team_external_id}, away={away_team_external_id}")
                return None
            
            # Parsear fecha
            match_date_str = match_data.get('date', match_data.get('match_date', ''))
            match_date = self._parse_date(match_date_str)
            
            if not match_date:
                logger.warning(f"Fecha inválida: {match_date_str}")
                return None
            
            return {
                'external_id': str(match_data.get('id', match_data.get('match_id'))),
                'home_team_id': home_team.id,
                'away_team_id': away_team.id,
                'league': match_data.get('league', match_data.get('competition', '')),
                'season': match_data.get('season', ''),
                'match_date': match_date,
                'status': match_data.get('status', 'scheduled').lower(),
                'home_score': match_data.get('home_score', match_data.get('score', {}).get('home')),
                'away_score': match_data.get('away_score', match_data.get('score', {}).get('away'))
            }
        except Exception as e:
            logger.error(f"Error transformando datos de partido: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _update_team(self, team: Team, new_data: Dict[str, Any]):
        for key, value in new_data.items():
            if hasattr(team, key) and value is not None:
                setattr(team, key, value)
        team.updated_at = datetime.utcnow()
    
    def _update_match(self, match: Match, new_data: Dict[str, Any]):
        for key, value in new_data.items():
            if hasattr(match, key) and value is not None:
                setattr(match, key, value)
        match.updated_at = datetime.utcnow()
    
    def _process_match_statistics(self, statistics: List[Dict], match_id: int, session: Session):
        for stat in statistics:
            try:
                team_external_id = str(stat.get('team_id', ''))
                team = session.query(Team).filter(Team.external_id == team_external_id).first()
                
                if team:
                    match_stat = MatchStatistic(
                        match_id=match_id,
                        team_id=team.id,
                        statistic_type=stat.get('type', ''),
                        value=float(stat.get('value', 0))
                    )
                    session.add(match_stat)
            except Exception as e:
                logger.error(f"Error procesando estadística: {e}")
    
    def process_all_pending(self) -> Dict[str, int]:
        logger.info("Iniciando procesamiento de todos los datos pendientes")
        
        results = {
            'teams_processed': self.transform_teams(),
            'matches_processed': self.transform_matches()
        }
        
        logger.info(f"Procesamiento completado: {results}")
        return results