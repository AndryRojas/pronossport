#!/usr/bin/env python3
"""
Script de prueba para el servicio de consultas RawQueryService
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_query_service():
    """Probar el servicio de consultas básicas"""
    print("🧪 Iniciando pruebas del RawQueryService...")
    
    try:
        # Importar el servicio
        from src.services.query_service import RawQueryService
        print("✅ RawQueryService importado correctamente")
        
        # Crear instancia del servicio
        query_service = RawQueryService()
        print("✅ Instancia de RawQueryService creada")
        
        # Probar método para obtener temporadas disponibles
        print("\n📅 Probando obtención de temporadas disponibles...")
        seasons = query_service.get_available_seasons()
        print(f"✅ Temporadas encontradas: {seasons}")
        
        # Probar consulta de resumen por país
        print("\n🌍 Probando resumen de ligas por país...")
        summary = query_service.get_leagues_summary_by_country()
        print(f"✅ Países encontrados: {len(summary) if summary else 0}")
        
        if summary:
            for country_data in summary[:3]:  # Mostrar solo los primeros 3
                print(f"  • {country_data['country']}: {country_data['total_leagues']} ligas")
        
        # Probar consulta completa de ligas
        print("\n🏆 Probando consulta de ligas...")
        leagues = query_service.get_leagues_by_country_and_season()
        print(f"✅ Ligas encontradas: {len(leagues) if leagues else 0}")
        
        if leagues:
            # Mostrar algunas ligas como ejemplo
            for league in leagues[:3]:  # Mostrar solo las primeras 3
                print(f"  • {league['country']}: {league['league_name']} (Temporada: {league['season']})")
        
        print("\n✅ Todas las pruebas completadas exitosamente!")
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que las dependencias estén instaladas")
        return False
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        print(f"💡 Tipo de error: {type(e).__name__}")
        return False

def test_database_connection():
    """Probar la conexión a la base de datos"""
    print("\n🔌 Probando conexión a la base de datos...")
    
    try:
        from src.database.connection import raw_db_manager
        
        # Probar conexión
        connection_ok = raw_db_manager.test_connection()
        
        if connection_ok:
            print("✅ Conexión a raw_pronossport exitosa")
            return True
        else:
            print("❌ Error en la conexión a raw_pronossport")
            return False
            
    except ImportError as e:
        print(f"❌ Error importando módulos de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error probando conexión: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Pronossport - Test del Servicio de Consultas")
    print("=" * 50)
    
    # Probar conexión primero
    db_ok = test_database_connection()
    
    if db_ok:
        # Si la conexión está bien, probar el servicio
        test_query_service()
    else:
        print("\n💡 Para probar el servicio completo, asegúrate de:")
        print("   1. Configurar el archivo .env con las credenciales de base de datos")
        print("   2. Tener acceso a la base de datos raw_pronossport")
        print("   3. Instalar las dependencias: pip install -r requirements.txt")
    
    print("\n🏁 Pruebas finalizadas")