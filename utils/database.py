import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create base class for declarative models
Base = declarative_base()

class College(Base):
    """SQLAlchemy model for college data"""
    __tablename__ = 'colleges'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String)
    state = Column(String)
    type = Column(String)
    in_state_tuition = Column(Float)
    out_state_tuition = Column(Float)
    admission_rate = Column(Float)
    enrollment = Column(Integer)
    graduation_rate = Column(Float)

class DatabaseConnection:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create SQLAlchemy engine
        self.engine = create_engine(self.database_url)
        
        # Create all tables
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_colleges(self, filters=None, sort_by=None, ascending=True):
        """
        Get colleges with optional filtering and sorting
        
        Args:
            filters (dict): Dictionary of filter conditions
            sort_by (str): Column name to sort by
            ascending (bool): Sort order
        """
        query = self.session.query(College)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(College, key) and value is not None:
                    if isinstance(value, tuple) and len(value) == 2:
                        # Range filter
                        min_val, max_val = value
                        if min_val is not None:
                            query = query.filter(getattr(College, key) >= min_val)
                        if max_val is not None:
                            query = query.filter(getattr(College, key) <= max_val)
                    else:
                        # Exact match filter
                        query = query.filter(getattr(College, key) == value)
        
        # Apply sorting
        if sort_by and hasattr(College, sort_by):
            query = query.order_by(
                getattr(College, sort_by).desc() if not ascending 
                else getattr(College, sort_by)
            )
        
        return query.all()

    def close(self):
        """Close the database session"""
        self.session.close()
