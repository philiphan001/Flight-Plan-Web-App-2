import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import os
from models.database import Institution, Program, AdmissionDetail

def init_connection():
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    return create_engine(database_url)

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
                'Institution Name': inst.name,
                'City': inst.city,
                'State': inst.state,
                'Type': inst.institution_type,
                'Website': inst.website,
                'Program': prog.name if prog else None,
                'Degree Level': prog.degree_level if prog else None,
                'Duration (Years)': prog.duration_years if prog else None,
                'In-State Tuition': prog.tuition_in_state if prog else None,
                'Out-of-State Tuition': prog.tuition_out_state if prog else None,
                'Admission Rate': adm.admission_rate if adm else None,
                'Avg SAT': adm.avg_sat_score if adm else None,
                'Avg ACT': adm.avg_act_score if adm else None,
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
        institution_types = [r[0] for r in session.query(Institution.institution_type).distinct()]
        states = [r[0] for r in session.query(Institution.state).distinct()]
        degree_levels = [r[0] for r in session.query(Program.degree_level).distinct()]
        session.close()
        
        # Filter inputs
        selected_type = st.sidebar.selectbox(
            "Institution Type",
            ["All"] + institution_types,
            index=0
        )
        
        selected_state = st.sidebar.selectbox(
            "State",
            ["All"] + states,
            index=0
        )
        
        selected_degree = st.sidebar.selectbox(
            "Degree Level",
            ["All"] + degree_levels,
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
            "Institution Name", "State", "Type", "Admission Rate",
            "In-State Tuition", "Out-of-State Tuition"
        ]
        sort_by = st.sidebar.selectbox("Sort by", sort_columns)
        sort_ascending = st.sidebar.checkbox("Ascending order", value=True)
        
        # Get and display data
        df = get_data(engine, filters, sort_by, sort_ascending)
        
        # Display summary statistics
        st.header("Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Institutions", len(df['Institution Name'].unique()))
        with col2:
            st.metric("States Represented", len(df['State'].unique()))
        with col3:
            avg_tuition = df['In-State Tuition'].mean()
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

if __name__ == "__main__":
    main()
