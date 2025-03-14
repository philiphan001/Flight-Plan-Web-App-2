import os
import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

def get_connection():
    """Create database connection using environment variables"""
    try:
        database_url = os.environ['DATABASE_URL']
        result = urlparse(database_url)
        
        conn = psycopg2.connect(
            dbname=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return None

def query_data(sql, params=None):
    """Execute a query and return results"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            data = cur.fetchall()
            return data
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return []
    finally:
        conn.close()

def init_database():
    """Initialize database tables if they don't exist"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            # Create institutions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS institutions (
                    unitid SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    city VARCHAR(100),
                    state VARCHAR(2),
                    zipcode VARCHAR(10),
                    institution_type VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create demographics table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS demographics (
                    id SERIAL PRIMARY KEY,
                    unitid INTEGER REFERENCES institutions(unitid),
                    year INTEGER,
                    total_enrollment INTEGER,
                    men INTEGER,
                    women INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Error initializing database: {str(e)}")
        return False
    finally:
        conn.close()
