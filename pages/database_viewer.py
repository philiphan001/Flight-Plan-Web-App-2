import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, select, pool
from sqlalchemy.orm import sessionmaker
import os
from models.database import Institution, Program, AdmissionDetail
from sqlalchemy.exc import OperationalError
import time

def init_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    # Handle special case for postgresql:// URLs
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Add SSL requirements and connection pooling
    if '?' not in database_url:
        database_url += '?'
    if 'sslmode=' not in database_url:
        database_url += '&sslmode=require'

    # Create engine with connection pooling
    return create_engine(
        database_url,
        poolclass=pool.QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800  # Recycle connections after 30 minutes
    )

def get_data_with_retry(engine, filters=None, sort_by=None, sort_ascending=True, max_retries=3):
    for attempt in range(max_retries):
        try:
            return get_data(engine, filters, sort_by, sort_ascending)
        except OperationalError as e:
            if attempt == max_retries - 1:  # Last attempt
                raise
            time.sleep(1 * (attempt + 1))  # Exponential backoff
            st.warning(f"Retrying database connection (attempt {attempt + 2}/{max_retries})...")
            continue

def get_data(engine, filters=None, sort_by=None, sort_ascending=True):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Start with a base query joining all tables
        query = (
            select(
                Institution,
                Program,
                AdmissionDetail
            )
            .join(Program, Institution.id == Program.institution_id, isouter=True)
            .join(AdmissionDetail, Institution.id == AdmissionDetail.institution_id, isouter=True)
        )

        # Apply filters
        if filters:
            for column, value in filters.items():
                if value:
                    if column == 'institution_type':
                        query = query.where(Institution.institution_type == value)
                    elif column == 'state':
                        query = query.where(Institution.state == value)
                    elif column == 'degree_level':
                        query = query.where(Program.degree_level == value)

        # Execute query and fetch results
        results = session.execute(query).fetchall()

        # Convert results to a list of dictionaries
        data = []
        for row in results:
            inst, prog, adm = row
            data.append({
                'name': inst.name,
                'city': inst.city,
                'state': inst.state,
                'institution_type': inst.institution_type,
                'website': inst.website,
                'program_name': prog.name if prog else None,
                'degree_level': prog.degree_level if prog else None,
                'duration_years': prog.duration_years if prog else None,
                'tuition_in_state': prog.tuition_in_state if prog else None,
                'tuition_out_state': prog.tuition_out_state if prog else None,
                'admission_rate': adm.admission_rate if adm else None,
                'avg_sat_score': adm.avg_sat_score if adm else None,
                'avg_act_score': adm.avg_act_score if adm else None,
            })

        # Convert to DataFrame for easy sorting
        df = pd.DataFrame(data)
        if sort_by and sort_by in df.columns:
            df = df.sort_values(by=sort_by, ascending=sort_ascending)

        return df

    finally:
        session.close()

def main():
    st.title("Educational Institutions Database Explorer 🎓")

    try:
        engine = init_connection()

        # Sidebar filters
        st.sidebar.header("Filters")

        # Get unique values for filter options
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            institution_types = [r[0] for r in session.query(Institution.institution_type).distinct()]
            states = [r[0] for r in session.query(Institution.state).distinct()]
            degree_levels = [r[0] for r in session.query(Program.degree_level).distinct()]
        finally:
            session.close()

        # Filter inputs
        selected_type = st.sidebar.selectbox(
            "Institution Type",
            ["All"] + (institution_types if institution_types else ["All"]),
            index=0
        )

        selected_state = st.sidebar.selectbox(
            "State",
            ["All"] + (states if states else ["All"]),
            index=0
        )

        selected_degree = st.sidebar.selectbox(
            "Degree Level",
            ["All"] + (degree_levels if degree_levels else ["All"]),
            index=0
        )

        # Create filters dictionary
        filters = {}
        if selected_type != "All":
            filters['institution_type'] = selected_type
        if selected_state != "All":
            filters['state'] = selected_state
        if selected_degree != "All":
            filters['degree_level'] = selected_degree

        # Sorting options
        st.sidebar.header("Sorting")
        sort_columns = [
            "name", "state", "institution_type", "admission_rate",
            "tuition_in_state", "tuition_out_state"
        ]
        sort_by = st.sidebar.selectbox("Sort by", sort_columns)
        sort_ascending = st.sidebar.checkbox("Ascending order", value=True)

        # Get and display data with retry mechanism
        df = get_data_with_retry(engine, filters, sort_by, sort_ascending)

        # Display summary statistics
        st.header("Summary Statistics")
        col1, col2, col3 = st.columns(3)

        # Check if DataFrame is empty
        if df.empty:
            st.warning("No data found with the current filters. Try adjusting your search criteria.")
        else:
            with col1:
                st.metric("Total Institutions", df['name'].nunique())
            with col2:
                st.metric("States Represented", df['state'].nunique())
            with col3:
                avg_tuition = df['tuition_in_state'].mean()
                st.metric("Avg In-State Tuition", f"${avg_tuition:,.2f}" if pd.notnull(avg_tuition) else "N/A")

            # Display the data
            st.header("Institutions Data")
            st.dataframe(df)

            # Add download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="educational_institutions.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please try refreshing the page. If the problem persists, contact support.")

if __name__ == "__main__":
    main()