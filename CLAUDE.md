# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pronossport is a Python application designed to extract sports data from external APIs and manage it across two MySQL databases:
- `raw_pronossport`: Stores raw API data
- `pronossport`: Stores transformed/processed data

## Architecture

The project follows a modular architecture with clear separation of concerns:

```
src/
├── api/           # API client for external data extraction
├── database/      # Database connection management
├── models/        # SQLAlchemy models for both databases
├── services/      # Business logic (extraction & transformation)
├── config/        # Configuration management
└── utils/         # Utility functions (logging)
```

## Database Structure

**Raw Database (raw_pronossport):**
- `raw_api_data`: Generic API responses
- `raw_matches`: Raw match data from API
- `raw_teams`: Raw team data from API
- `extraction_logs`: Extraction process logs

**Processed Database (pronossport):**
- `teams`: Cleaned team information
- `matches`: Processed match data
- `match_statistics`: Match statistics
- `predictions`: Prediction data
- `processing_logs`: Transformation logs

## Common Commands

**Setup:**
- `python -m venv venv` - Create virtual environment
- `source venv/bin/activate` - Activate environment (Linux/Mac)
- `pip install -r requirements.txt` - Install dependencies
- `cp .env.example .env` - Create environment file (configure with your settings)

**Database Operations:**
- `python main.py test-connections` - Test database connections
- `python main.py create-tables` - Create database tables
- `python main.py status` - Show system status

**Data Operations:**
- `python main.py extract --endpoint matches` - Extract match data
- `python main.py extract --endpoint teams` - Extract team data
- `python main.py transform` - Transform raw data
- `python main.py extract-and-transform` - Full extraction and transformation
- `python main.py daily-extraction` - Extract today and tomorrow's matches

## Configuration

Environment variables are managed in `.env` file (copy from `.env.example`):
- Database connections for both raw and processed databases
- API configuration (base URL, key, timeout)
- Processing settings (batch sizes, retry attempts)
- Logging configuration

## Key Classes

- `APIClient`: Handles external API communication with retry logic
- `ExtractionService`: Manages data extraction from API to raw database
- `TransformationService`: Processes raw data into structured format
- `DatabaseManager`: Manages database connections and sessions

## Development Notes

- Uses SQLAlchemy ORM for database operations
- Implements dual database pattern (raw → processed)
- Includes comprehensive logging with loguru
- Built-in retry mechanisms for API calls
- Batch processing for large datasets
- CLI interface using click for easy operation