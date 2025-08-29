#!/usr/bin/env python3
"""
Aplicación web Flask para visualizar datos de Pronossport
Interfaz visual para consultar ligas, equipos, jugadores y partidos
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
from src.services.query_service import RawQueryService
from src.services.web_query_service import WebQueryService
from src.utils.logger import logger

def create_app():
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = 'pronossport-dashboard-2024'
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Habilitar CORS para desarrollo
    CORS(app)
    
    # Configurar ruta de templates y archivos estáticos
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    
    app.template_folder = template_dir
    app.static_folder = static_dir
    
    # Inicializar servicios
    query_service = RawQueryService()
    web_service = WebQueryService()
    
    # ========================================
    # RUTAS PRINCIPALES
    # ========================================
    
    @app.route('/')
    def index():
        """Página principal del dashboard"""
        try:
            # Obtener estadísticas básicas
            stats = web_service.get_dashboard_stats()
            return render_template('index.html', stats=stats)
        except Exception as e:
            logger.error(f"Error cargando dashboard: {e}")
            return render_template('index.html', stats={}, error=str(e))
    
    @app.route('/leagues')
    def leagues():
        """Página de ligas"""
        try:
            # Obtener parámetros de filtro y paginación
            season = request.args.get('season')
            country = request.args.get('country')
            page = int(request.args.get('page', 1))
            per_page = 50  # Registros por página
            
            # Obtener datos de ligas con paginación
            leagues_data, pagination_info = query_service.get_leagues_by_country_and_season(season, country, page, per_page)
            countries = web_service.get_available_countries()
            seasons = query_service.get_available_seasons()
            
            return render_template('leagues.html', 
                                 leagues=leagues_data,
                                 countries=countries,
                                 seasons=seasons,
                                 current_season=season,
                                 current_country=country,
                                 pagination=pagination_info)
        except Exception as e:
            logger.error(f"Error cargando ligas: {e}")
            return render_template('leagues.html', error=str(e))
    
    @app.route('/teams')
    def teams():
        """Página de equipos"""
        try:
            # Obtener parámetros de filtro y paginación
            league_id = request.args.get('league_id')
            season = request.args.get('season')
            country = request.args.get('country')
            page = int(request.args.get('page', 1))
            per_page = 50  # Registros por página
            
            # Obtener datos de equipos con paginación
            teams_data, pagination_info = web_service.get_teams_summary(league_id=league_id, season=season, country=country, page=page, per_page=per_page)
            leagues = web_service.get_leagues_for_filter()
            seasons = query_service.get_available_seasons()
            
            return render_template('teams.html',
                                 teams=teams_data,
                                 leagues=leagues,
                                 seasons=seasons,
                                 current_league=league_id,
                                 current_season=season,
                                 current_country=country,
                                 pagination=pagination_info)
        except Exception as e:
            logger.error(f"Error cargando equipos: {e}")
            return render_template('teams.html', error=str(e))
    
    @app.route('/players')
    def players():
        """Página de jugadores"""
        try:
            # Obtener parámetros de filtro y paginación
            team_id = request.args.get('team_id')
            league_id = request.args.get('league_id')
            season = request.args.get('season')
            page = int(request.args.get('page', 1))
            per_page = 50  # Registros por página
            
            # Obtener datos de jugadores con paginación
            players_data, pagination_info = web_service.get_players_summary(team_id=team_id, league_id=league_id, season=season, page=page, per_page=per_page)
            teams = web_service.get_teams_for_filter()
            leagues = web_service.get_leagues_for_filter()
            seasons = web_service.get_available_seasons_for_players()
            
            return render_template('players.html',
                                 players=players_data,
                                 teams=teams,
                                 leagues=leagues,
                                 seasons=seasons,
                                 current_team=team_id,
                                 current_league=league_id,
                                 current_season=season,
                                 pagination=pagination_info)
        except Exception as e:
            logger.error(f"Error cargando jugadores: {e}")
            return render_template('players.html', error=str(e))
    
    @app.route('/matches')
    def matches():
        """Página de partidos"""
        try:
            # Obtener parámetros de filtro y paginación
            league_id = request.args.get('league_id')
            season = request.args.get('season')
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            page = int(request.args.get('page', 1))
            per_page = 50  # Registros por página
            
            # Obtener datos de partidos con paginación
            matches_data, pagination_info = web_service.get_matches_summary(
                league_id=league_id, 
                season=season,
                date_from=date_from,
                date_to=date_to,
                page=page,
                per_page=per_page
            )
            leagues = web_service.get_leagues_for_filter()
            seasons = query_service.get_available_seasons()
            
            return render_template('matches.html',
                                 matches=matches_data,
                                 leagues=leagues,
                                 seasons=seasons,
                                 current_league=league_id,
                                 current_season=season,
                                 current_date_from=date_from,
                                 current_date_to=date_to,
                                 pagination=pagination_info)
        except Exception as e:
            logger.error(f"Error cargando partidos: {e}")
            return render_template('matches.html', error=str(e))
    
    @app.route('/administration')
    def administration():
        """Página de administración de datos"""
        try:
            # Obtener parámetros de filtro con England como default
            country_filter = request.args.get('country', 'England')
            league_filter = request.args.get('league_name', '')
            season_filter = request.args.get('season', '')
            leagues_filter = request.args.get('leagues_filter', 'all')  # 'all' o 'no_data'
            teams_filter = request.args.get('teams_filter', 'all')     # 'all' o 'no_data'
            selected_league = request.args.get('league_id')
            
            # Obtener datos para los filtros
            countries = web_service.get_administration_countries()
            leagues_by_country = []
            seasons_by_league = []
            
            if country_filter:
                leagues_by_country = web_service.get_administration_leagues_by_country(country_filter)
                
                if league_filter:
                    seasons_by_league = web_service.get_administration_seasons_by_league(league_filter, country_filter)
            
            # Obtener datos de ligas con filtros aplicados
            leagues_data = web_service.get_administration_leagues_data(
                filter_type=leagues_filter,
                country=country_filter,
                league_name=league_filter if league_filter else None,
                season=season_filter if season_filter else None
            )
            
            # Obtener datos de equipos si hay liga seleccionada
            teams_data = []
            league_details = None
            if selected_league:
                teams_data = web_service.get_administration_teams_data(selected_league, teams_filter, season_filter)
                league_details = web_service.get_league_details_for_admin(selected_league)
            
            return render_template('administration.html',
                                 leagues=leagues_data,
                                 teams=teams_data,
                                 league_details=league_details,
                                 selected_league=selected_league,
                                 leagues_filter=leagues_filter,
                                 teams_filter=teams_filter,
                                 countries=countries,
                                 leagues_by_country=leagues_by_country,
                                 seasons_by_league=seasons_by_league,
                                 current_country=country_filter,
                                 current_league=league_filter,
                                 current_season=season_filter)
        except Exception as e:
            logger.error(f"Error cargando administración: {e}")
            return render_template('administration.html', error=str(e))
    
    # ========================================
    # API ENDPOINTS
    # ========================================
    
    @app.route('/api/leagues')
    def api_leagues():
        """API endpoint para obtener ligas"""
        try:
            season = request.args.get('season')
            country = request.args.get('country')
            
            if country:
                data = query_service.get_leagues_by_country(country, season)
            else:
                data = query_service.get_leagues_by_country_and_season(season)
            
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/teams')
    def api_teams():
        """API endpoint para obtener equipos"""
        try:
            league_id = request.args.get('league_id')
            season = request.args.get('season')
            country = request.args.get('country')
            
            data = web_service.get_teams_summary(league_id=league_id, season=season, country=country)
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/players')
    def api_players():
        """API endpoint para obtener jugadores"""
        try:
            team_id = request.args.get('team_id')
            league_id = request.args.get('league_id')
            season = request.args.get('season')
            
            data = web_service.get_players_summary(team_id=team_id, league_id=league_id, season=season)
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/matches')
    def api_matches():
        """API endpoint para obtener partidos"""
        try:
            league_id = request.args.get('league_id')
            season = request.args.get('season')
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            
            data = web_service.get_matches_summary(
                league_id=league_id,
                season=season,
                date_from=date_from,
                date_to=date_to
            )
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/stats')
    def api_stats():
        """API endpoint para estadísticas del dashboard"""
        try:
            stats = web_service.get_dashboard_stats()
            return jsonify({'success': True, 'data': stats})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/administration/leagues')
    def api_administration_leagues():
        """API endpoint para datos de administración de ligas"""
        try:
            filter_type = request.args.get('filter', 'all')
            data = web_service.get_administration_leagues_data(filter_type)
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/administration/teams/<league_id>')
    def api_administration_teams(league_id):
        """API endpoint para datos de administración de equipos"""
        try:
            filter_type = request.args.get('filter', 'all')
            season = request.args.get('season')
            data = web_service.get_administration_teams_data(league_id, filter_type, season)
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/administration/leagues-by-country/<country>')
    def api_administration_leagues_by_country(country):
        """API endpoint para obtener ligas por país"""
        try:
            data = web_service.get_administration_leagues_by_country(country)
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/administration/seasons-by-league')
    def api_administration_seasons_by_league():
        """API endpoint para obtener temporadas por liga"""
        try:
            league_name = request.args.get('league_name')
            country = request.args.get('country')
            
            if not league_name or not country:
                return jsonify({'success': False, 'error': 'league_name y country son requeridos'}), 400
            
            data = web_service.get_administration_seasons_by_league(league_name, country)
            return jsonify({'success': True, 'data': data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ========================================
    # MANEJADORES DE ERRORES
    # ========================================
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', 
                             error_code=404, 
                             error_message="Página no encontrada"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', 
                             error_code=500, 
                             error_message="Error interno del servidor"), 500
    
    # ========================================
    # FILTROS PERSONALIZADOS PARA TEMPLATES
    # ========================================
    
    @app.template_filter('format_date')
    def format_date(date_string):
        """Filtro para formatear fechas"""
        if not date_string:
            return "N/A"
        try:
            if isinstance(date_string, str):
                date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            else:
                date_obj = date_string
            return date_obj.strftime('%d/%m/%Y')
        except:
            return date_string
    
    @app.template_filter('format_datetime')
    def format_datetime(date_string):
        """Filtro para formatear fecha y hora"""
        if not date_string:
            return "N/A"
        try:
            if isinstance(date_string, str):
                date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            else:
                date_obj = date_string
            return date_obj.strftime('%d/%m/%Y %H:%M')
        except:
            return date_string
    
    @app.template_global()
    def build_pagination_url(page_num):
        """Construye URL con paginación manteniendo los filtros actuales"""
        from urllib.parse import urlencode
        args = dict(request.args)
        args['page'] = page_num
        query_string = urlencode(args)
        return f"{request.path}?{query_string}"
    
    return app

# Para desarrollo directo
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)