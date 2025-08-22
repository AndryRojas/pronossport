#!/usr/bin/env python3
import click
from datetime import datetime, timedelta
from src.utils.logger import logger
from src.database.connection import raw_db_manager, pronos_db_manager
from src.services.extraction_service import ExtractionService
from src.services.transformation_service import TransformationService
from src.services.query_service import RawQueryService
from src.models.raw_models import RawBase
from src.models.pronos_models import PronosBase

@click.group()
def cli():
    """Pronossport API Extractor - Herramienta para extraer y procesar datos deportivos"""
    pass

@cli.command()
def test_connections():
    """Probar las conexiones a ambas bases de datos"""
    logger.info("Probando conexiones a las bases de datos...")
    
    raw_connection = raw_db_manager.test_connection()
    pronos_connection = pronos_db_manager.test_connection()
    
    if raw_connection and pronos_connection:
        logger.info("✅ Todas las conexiones exitosas")
        return True
    else:
        logger.error("❌ Error en las conexiones")
        return False

@cli.command()
def create_tables():
    """Crear tablas en ambas bases de datos"""
    try:
        logger.info("Creando tablas en raw_pronossport...")
        RawBase.metadata.create_all(raw_db_manager.engine)
        
        logger.info("Creando tablas en pronossport...")
        PronosBase.metadata.create_all(pronos_db_manager.engine)
        
        logger.info("✅ Tablas creadas exitosamente")
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {e}")

@cli.command()
@click.option('--endpoint', default='fixtures', help='Endpoint de la API a consultar')
@click.option('--date-from', help='Fecha desde (YYYY-MM-DD)')
@click.option('--date-to', help='Fecha hasta (YYYY-MM-DD)')
@click.option('--date', help='Fecha específica (YYYY-MM-DD)')
@click.option('--league', type=int, help='ID de la liga')
@click.option('--season', type=int, help='Temporada (YYYY)')
@click.option('--country', help='Código del país para ligas')
def extract(endpoint, date_from, date_to, date, league, season, country):
    """Extraer datos de la API-Sports"""
    logger.info(f"Iniciando extracción de {endpoint}...")
    
    extraction_service = ExtractionService()
    
    try:
        if endpoint == 'fixtures':
            success = extraction_service.extract_football_fixtures(
                date=date, league=league, season=season, 
                date_from=date_from, date_to=date_to
            )
        elif endpoint == 'teams':
            success = extraction_service.extract_football_teams(
                league=league, season=season
            )
        elif endpoint == 'leagues':
            success = extraction_service.extract_football_leagues(
                country=country, season=season
            )
        elif endpoint == 'standings':
            if not league or not season:
                logger.error("Para standings necesitas especificar --league y --season")
                return
            success = extraction_service.extract_football_standings(
                league=league, season=season
            )
        else:
            success = extraction_service.extract_and_store(endpoint)
        
        if success:
            logger.info("✅ Extracción completada exitosamente")
        else:
            logger.error("❌ Error en la extracción")
            
    except Exception as e:
        logger.error(f"❌ Error durante la extracción: {e}")

@cli.command()
@click.option('--batch-size', default=100, help='Tamaño del lote para procesamiento')
def transform(batch_size):
    """Transformar datos raw a formato estructurado"""
    logger.info("Iniciando transformación de datos...")
    
    transformation_service = TransformationService()
    
    try:
        results = transformation_service.process_all_pending()
        logger.info(f"✅ Transformación completada: {results}")
    except Exception as e:
        logger.error(f"❌ Error durante la transformación: {e}")

@cli.command()
@click.option('--date-from', help='Fecha desde (YYYY-MM-DD)')
@click.option('--date-to', help='Fecha hasta (YYYY-MM-DD)')
@click.option('--batch-size', default=100, help='Tamaño del lote')
def extract_and_transform(date_from, date_to, batch_size):
    """Ejecutar proceso completo: extracción y transformación"""
    logger.info("Iniciando proceso completo de extracción y transformación...")
    
    extraction_service = ExtractionService()
    transformation_service = TransformationService()
    
    try:
        # 1. Extraer equipos
        logger.info("Extrayendo equipos...")
        extraction_service.extract_teams()
        
        # 2. Procesar equipos
        logger.info("Procesando equipos...")
        transformation_service.transform_teams(batch_size)
        
        # 3. Extraer partidos
        logger.info("Extrayendo partidos...")
        extraction_service.extract_matches(date_from, date_to)
        
        # 4. Procesar partidos
        logger.info("Procesando partidos...")
        transformation_service.transform_matches(batch_size)
        
        logger.info("✅ Proceso completo finalizado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error en el proceso completo: {e}")

@cli.command()
@click.option('--league', type=int, help='ID de liga específica (opcional)')
@click.option('--season', type=int, help='Temporada específica (opcional)')
def daily_extraction(league, season):
    """Ejecutar extracción diaria (hoy y mañana)"""
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    current_season = datetime.now().year
    
    logger.info(f"Iniciando extracción diaria para {today} - {tomorrow}")
    
    extraction_service = ExtractionService()
    transformation_service = TransformationService()
    
    try:
        # Extraer partidos de hoy y mañana
        extraction_service.extract_football_fixtures(
            date_from=today, 
            date_to=tomorrow,
            league=league,
            season=season or current_season
        )
        
        # Si se especifica una liga, extraer también equipos y standings
        if league:
            extraction_service.extract_football_teams(
                league=league, 
                season=season or current_season
            )
            extraction_service.extract_football_standings(
                league=league, 
                season=season or current_season
            )
        
        # Procesar datos (mantenemos la transformación original)
        transformation_service.transform_matches()
        
        logger.info("✅ Extracción diaria completada")
        
    except Exception as e:
        logger.error(f"❌ Error en extracción diaria: {e}")

@cli.command()
@click.option('--endpoint', default='countries', help='Endpoint a probar')
@click.option('--country', help='Código del país')
@click.option('--season', type=int, help='Temporada')
@click.option('--league', type=int, help='ID de liga')
def debug_api(endpoint, country, season, league):
    """Debug - Ver datos raw de API-Sports"""
    logger.info(f"Debug API-Sports endpoint: {endpoint}")
    
    try:
        from src.api.client import APIClient
        import json
        client = APIClient()
        
        data = None
        
        if endpoint == 'countries':
            data = client.get_countries()
        elif endpoint == 'leagues':
            data = client.get_leagues(country=country, season=season)
        elif endpoint == 'fixtures':
            data = client.get_fixtures(league=league, season=season)
        elif endpoint == 'teams':
            data = client.get_teams(league=league, season=season)
        elif endpoint == 'standings':
            if league and season:
                data = client.get_standings(league=league, season=season)
        
        if data:
            logger.info(f"✅ Respuesta recibida!")
            logger.info(f"Keys principales: {list(data.keys())}")
            
            if 'response' in data:
                response_data = data['response']
                logger.info(f"Elementos en response: {len(response_data)}")
                
                if response_data and len(response_data) > 0:
                    logger.info("📋 Primer elemento:")
                    print(json.dumps(response_data[0], indent=2, ensure_ascii=False))
                else:
                    logger.warning("❌ Response está vacío")
            
            logger.info("📊 Datos completos disponibles para análisis")
        else:
            logger.error("❌ No se recibieron datos")
            
    except Exception as e:
        logger.error(f"❌ Error en debug: {e}")

@cli.command()
def test_api():
    """Probar conexión a API-Sports"""
    logger.info("Probando conexión a API-Sports...")
    
    try:
        from src.api.client import APIClient
        client = APIClient()
        
        # Probar obtener países
        countries = client.get_countries()
        
        if countries and 'response' in countries:
            logger.info(f"✅ API-Sports conectada exitosamente!")
            logger.info(f"Países disponibles: {len(countries['response'])}")
            
            # Mostrar algunos países como ejemplo
            for i, country in enumerate(countries['response'][:5]):
                logger.info(f"  - {country['name']} ({country['code']})")
            
            return True
        else:
            logger.error("❌ Error en respuesta de API-Sports")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error conectando a API-Sports: {e}")
        return False

@cli.command()
@click.option('--country', help='País de las ligas (ej: England)')
@click.option('--league-id', help='Id de la liga (ej: 34)')
@click.option('--season-from', type=int, default=2018, help='Temporada inicial (default: 2018)')
@click.option('--season-to', type=int, default=2025, help='Temporada final (default: 2025)')
def extract_teams_from_db(country, league_id, season_from, season_to):
    """Extraer equipos desde ligas guardadas en base de datos"""
    logger.info(f"🚀 Iniciando extracción masiva de equipos...")
    logger.info(f"📅 Rango: {season_from} - {season_to}")
    if country:
        logger.info(f"🌍 País: {country}")
    
    extraction_service = ExtractionService()
    
    try:
        success = extraction_service.extract_teams_from_leagues_db(
            country=country,
            league_id=league_id,
            season_from=season_from,
            season_to=season_to
        )
        
        if success:
            logger.info("✅ Extracción masiva completada exitosamente")
        else:
            logger.error("❌ Error en la extracción masiva")
            
    except Exception as e:
        logger.error(f"❌ Error durante la extracción masiva: {e}")

@cli.command()
@click.option('--country', help='País para mostrar resumen (opcional)')
def leagues_summary(country):
    """Mostrar resumen de ligas disponibles en base de datos"""
    logger.info("📊 Obteniendo resumen de ligas...")
    
    extraction_service = ExtractionService()
    
    try:
        extraction_service.get_leagues_summary(country=country)
    except Exception as e:
        logger.error(f"❌ Error obteniendo resumen: {e}")

@cli.command()
@click.option('--league-id', type=int, required=True, help='ID de la liga (ej: 39 para Premier League)')
@click.option('--season', type=int, required=True, help='Temporada (ej: 2018)')
@click.option('--team-id', type=int, help='ID del equipo específico (opcional)')
def extract_players(league_id, season, team_id):
    """Extraer jugadores con estadísticas por liga y temporada"""
    logger.info(f"🏃‍♂️ Iniciando extracción de jugadores...")
    logger.info(f"🏆 Liga: {league_id}")
    logger.info(f"📅 Temporada: {season}")
    if team_id:
        logger.info(f"⚽ Equipo: {team_id}")
    
    extraction_service = ExtractionService()
    
    try:
        success = extraction_service.extract_players_by_league_season(
            league_id=league_id,
            season=season,
            team_id=team_id
        )
        
        if success:
            logger.info("✅ Extracción de jugadores completada exitosamente")
        else:
            logger.error("❌ Error en la extracción de jugadores")
            
    except Exception as e:
        logger.error(f"❌ Error durante la extracción de jugadores: {e}")

@cli.command()
@click.option('--league-id', type=int, required=True, help='ID de la liga')
@click.option('--season', type=int, required=True, help='Temporada')
@click.option('--team-id', type=int, help='ID del equipo (opcional)')
def debug_players_pagination(league_id, season, team_id):
    """Debug - Ver información de paginación de jugadores"""
    logger.info(f"🔍 Debug paginación de jugadores...")
    logger.info(f"🏆 Liga: {league_id}, 📅 Temporada: {season}")
    if team_id:
        logger.info(f"⚽ Equipo: {team_id}")
    
    try:
        from src.api.client import APIClient
        import json
        client = APIClient()
        
        # Solo obtener primera página para ver paginación
        data = client.get_players(league=league_id, season=season, team=team_id, page=1)
        
        if data:
            logger.info(f"✅ Respuesta recibida!")
            logger.info(f"Keys principales: {list(data.keys())}")
            
            if 'paging' in data:
                paging = data['paging']
                logger.info(f"📊 Información de paginación:")
                logger.info(f"  📄 Página actual: {paging.get('current')}")
                logger.info(f"  📄 Total páginas: {paging.get('total')}")
                
            if 'results' in data:
                logger.info(f"📈 Resultados en esta página: {data['results']}")
                
            if 'response' in data:
                response_data = data['response']
                logger.info(f"🏃‍♂️ Jugadores en página 1: {len(response_data)}")
                
                if response_data and len(response_data) > 0:
                    logger.info("👤 Primer jugador de ejemplo:")
                    first_player = response_data[0]
                    player_info = first_player.get('player', {})
                    stats = first_player.get('statistics', [{}])[0] if first_player.get('statistics') else {}
                    team_info = stats.get('team', {})
                    games = stats.get('games', {})
                    
                    logger.info(f"  Nombre: {player_info.get('name')}")
                    logger.info(f"  Posición: {games.get('position')}")
                    logger.info(f"  Equipo: {team_info.get('name')}")
                    logger.info(f"  Apariciones: {games.get('appearences')}")
        else:
            logger.error("❌ No se recibieron datos")
            
    except Exception as e:
        logger.error(f"❌ Error en debug: {e}")

@cli.command()
@click.option('--league-id', type=int, required=True, help='ID de la liga')
@click.option('--season', type=int, required=True, help='Temporada')
def extract_fixtures(league_id, season):
    """Extraer fixtures de una liga y temporada específica"""
    logger.info(f"⚽ Iniciando extracción de fixtures...")
    logger.info(f"🏆 Liga: {league_id}")
    logger.info(f"📅 Temporada: {season}")
    
    try:
        from src.services.extraction_service import ExtractionService
        extraction_service = ExtractionService()
        
        success = extraction_service.extract_fixtures_by_league_season(
            league_id=league_id,
            season=season
        )
        
        if success:
            logger.info("✅ Extracción de fixtures completada exitosamente")
        else:
            logger.error("❌ Error en la extracción de fixtures")
            
    except Exception as e:
        logger.error(f"❌ Error durante la extracción de fixtures: {e}")

@cli.command()
def status():
    """Mostrar estado del sistema"""
    logger.info("Estado del sistema Pronossport:")
    
    try:
        # Probar conexiones
        raw_ok = raw_db_manager.test_connection()
        pronos_ok = pronos_db_manager.test_connection()
        
        logger.info(f"Conexión RAW DB: {'✅ OK' if raw_ok else '❌ Error'}")
        logger.info(f"Conexión PRONOS DB: {'✅ OK' if pronos_ok else '❌ Error'}")
        
        # Contar registros pendientes de procesar
        with raw_db_manager.get_session() as session:
            from src.models.raw_models import RawMatchData, RawTeamData
            
            pending_matches = session.query(RawMatchData).filter(RawMatchData.processed == 0).count()
            pending_teams = session.query(RawTeamData).filter(RawTeamData.processed == 0).count()
            
            logger.info(f"Partidos pendientes: {pending_matches}")
            logger.info(f"Equipos pendientes: {pending_teams}")
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")

@cli.group()
def query():
    """Consultas a la base de datos raw_pronossport"""
    pass

@query.command('leagues')
@click.option('--season', help='Filtrar por temporada (ej: 2024)')
@click.option('--country', help='Filtrar por país específico')
@click.option('--summary', is_flag=True, help='Mostrar solo resumen por país')
@click.option('--external-id', help='Obtener detalles de una liga específica por external_id')
def query_leagues(season, country, summary, external_id):
    """Consultar ligas agrupadas por país y liga"""
    logger.info("🔍 Consultando ligas de la base de datos...")
    
    try:
        query_service = RawQueryService()
        
        if external_id:
            # Consultar detalles de una liga específica
            league_details = query_service.get_league_details(external_id)
            if league_details:
                logger.info(f"📋 Detalles de la liga {external_id}:")
                logger.info(f"  Nombre: {league_details['name']}")
                logger.info(f"  País: {league_details['country']} ({league_details['country_code']})")
                logger.info(f"  Temporada: {league_details['season']}")
                logger.info(f"  Inicio: {league_details['season_start']}")
                logger.info(f"  Fin: {league_details['season_end']}")
                logger.info(f"  API Source: {league_details['api_source']}")
                if league_details['logo_url']:
                    logger.info(f"  Logo: {league_details['logo_url']}")
            else:
                logger.warning(f"❌ No se encontró liga con external_id: {external_id}")
            return
        
        if summary:
            # Mostrar resumen por país
            summary_data = query_service.get_leagues_summary_by_country(season)
            
            if summary_data:
                logger.info(f"📊 Resumen de ligas por país:")
                if season:
                    logger.info(f"📅 Temporada filtrada: {season}")
                
                total_countries = len(summary_data)
                total_leagues = sum(item['total_leagues'] for item in summary_data)
                total_records = sum(item['total_records'] for item in summary_data)
                
                logger.info(f"🌍 Total países: {total_countries}")
                logger.info(f"🏆 Total ligas únicas: {total_leagues}")
                logger.info(f"📝 Total registros: {total_records}")
                logger.info("---")
                
                for item in summary_data:
                    logger.info(f"🌍 {item['country']} ({item['country_code']}): {item['total_leagues']} ligas, {item['total_records']} registros")
            else:
                logger.warning("❌ No se encontraron datos de ligas")
                
        elif country:
            # Mostrar ligas de un país específico
            leagues_data = query_service.get_leagues_by_country(country, season)
            
            if leagues_data:
                logger.info(f"🏆 Ligas de {country}:")
                if season:
                    logger.info(f"📅 Temporada filtrada: {season}")
                
                for league in leagues_data:
                    logger.info(f"  • {league['name']} (ID: {league['external_id']}) - Temporada: {league['season']}")
                    
                logger.info(f"📊 Total: {len(leagues_data)} ligas encontradas")
            else:
                logger.warning(f"❌ No se encontraron ligas para {country}")
                
        else:
            # Mostrar todas las ligas agrupadas
            leagues_data = query_service.get_leagues_by_country_and_season(season)
            
            if leagues_data:
                logger.info("🏆 Ligas agrupadas por país:")
                if season:
                    logger.info(f"📅 Temporada filtrada: {season}")
                
                current_country = None
                country_count = 0
                total_leagues = 0
                
                for league in leagues_data:
                    if current_country != league['country']:
                        if current_country is not None:
                            logger.info(f"    Total: {country_count} ligas")
                        current_country = league['country']
                        country_count = 0
                        logger.info(f"\n🌍 {league['country']} ({league['country_code']}):")
                    
                    country_count += 1
                    total_leagues += 1
                    logger.info(f"  • {league['league_name']} (ID: {league['external_id']}) - Temporada: {league['season']}")
                
                if current_country is not None:
                    logger.info(f"    Total: {country_count} ligas")
                
                logger.info(f"\n📊 Total general: {total_leagues} ligas encontradas")
            else:
                logger.warning("❌ No se encontraron ligas")
                
        # Mostrar temporadas disponibles
        seasons = query_service.get_available_seasons()
        if seasons:
            logger.info(f"\n📅 Temporadas disponibles: {', '.join(seasons)}")
        
    except Exception as e:
        logger.error(f"❌ Error consultando ligas: {e}")

if __name__ == '__main__':
    cli()