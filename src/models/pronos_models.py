from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

PronosBase = declarative_base()

class Team(PronosBase):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(100), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    short_name = Column(String(10))
    country = Column(String(100))
    league = Column(String(255))
    logo_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', league='{self.league}')>"

class Match(PronosBase):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(100), nullable=False, unique=True)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    league = Column(String(255))
    season = Column(String(50))
    match_date = Column(DateTime, nullable=False)
    status = Column(String(50))  # 'scheduled', 'live', 'finished', 'cancelled'
    home_score = Column(Integer)
    away_score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    
    def __repr__(self):
        return f"<Match(id={self.id}, external_id='{self.external_id}', status='{self.status}')>"

class MatchStatistic(PronosBase):
    __tablename__ = 'match_statistics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    statistic_type = Column(String(100), nullable=False)  # 'possession', 'shots', 'corners', etc.
    value = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    match = relationship("Match")
    team = relationship("Team")
    
    def __repr__(self):
        return f"<MatchStatistic(match_id={self.match_id}, type='{self.statistic_type}', value={self.value})>"

class Prediction(PronosBase):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    prediction_type = Column(String(100), nullable=False)  # 'winner', 'total_goals', 'handicap', etc.
    predicted_value = Column(String(100))
    confidence = Column(Float)  # 0.0 to 1.0
    algorithm_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    match = relationship("Match")
    
    def __repr__(self):
        return f"<Prediction(match_id={self.match_id}, type='{self.prediction_type}', confidence={self.confidence})>"

class ProcessingLog(PronosBase):
    __tablename__ = 'processing_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_table = Column(String(100), nullable=False)
    raw_record_id = Column(Integer, nullable=False)
    processed_table = Column(String(100))
    processed_record_id = Column(Integer)
    processing_status = Column(String(50))  # 'success', 'error', 'skipped'
    error_message = Column(Text)
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProcessingLog(id={self.id}, status='{self.processing_status}')>"