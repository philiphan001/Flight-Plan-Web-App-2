from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os
from datetime import datetime

Base = declarative_base()

class Institution(Base):
    __tablename__ = 'institutions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    institution_type = Column(String, nullable=False)  # 4-year, 2-year, vocational
    website = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    programs = relationship("Program", back_populates="institution")
    admission_details = relationship("AdmissionDetail", back_populates="institution")

class Program(Base):
    __tablename__ = 'programs'
    
    id = Column(Integer, primary_key=True)
    institution_id = Column(Integer, ForeignKey('institutions.id'), nullable=False)
    name = Column(String, nullable=False)
    degree_level = Column(String, nullable=False)  # Bachelor's, Associate's, Certificate
    duration_years = Column(Float, nullable=False)
    tuition_in_state = Column(Float)
    tuition_out_state = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    institution = relationship("Institution", back_populates="programs")

class AdmissionDetail(Base):
    __tablename__ = 'admission_details'
    
    id = Column(Integer, primary_key=True)
    institution_id = Column(Integer, ForeignKey('institutions.id'), nullable=False)
    admission_rate = Column(Float)
    avg_sat_score = Column(Integer)
    avg_act_score = Column(Integer)
    application_deadline = Column(DateTime)
    requirements = Column(String)  # JSON string of requirements
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    institution = relationship("Institution", back_populates="admission_details")

# Create tables
def init_db():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Handle special case for postgresql:// URLs
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
