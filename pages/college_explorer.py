import streamlit as st
import pandas as pd
from utils.database import DatabaseConnection

def show_college_explorer():
    st.title("College Data Explorer 🎓")
    st.write("Filter and sort through college data")

    try:
        # Initialize database connection
        db = DatabaseConnection()

        # Sidebar filters
        st.sidebar.header("Filters")

        # State filter
        state = st.sidebar.text_input("State (e.g., CA, NY)")

        # Tuition range filter
        st.sidebar.subheader("Tuition Range")
        min_tuition, max_tuition = st.sidebar.slider(
            "In-State Tuition ($)",
            0, 100000, (0, 100000),
            step=1000
        )

        # Acceptance rate filter
        st.sidebar.subheader("Acceptance Rate")
        min_rate, max_rate = st.sidebar.slider(
            "Acceptance Rate (%)",
            0.0, 100.0, (0.0, 100.0),
            step=1.0
        )

        # Enrollment range
        st.sidebar.subheader("Enrollment")
        min_enrollment, max_enrollment = st.sidebar.slider(
            "Total Enrollment",
            0, 50000, (0, 50000),
            step=1000
        )

        # College type filter
        college_type = st.sidebar.selectbox(
            "College Type",
            ["All", "Public", "Private", "Community College"]
        )

        # Sorting options
        sort_by = st.sidebar.selectbox(
            "Sort by",
            ["name", "tuition_in", "tuition_out", "acceptance_rate", "enrollment", "graduation_rate"]
        )
        sort_order = st.sidebar.radio("Sort order", ["Ascending", "Descending"])

        # Create filters dictionary
        filters = {
            "state": state if state else None,
            "tuition_in": (min_tuition, max_tuition),
            "acceptance_rate": (min_rate/100, max_rate/100),
            "enrollment": (min_enrollment, max_enrollment)
        }

        # Add type filter if not "All"
        if college_type != "All":
            filters["type"] = college_type

        # Get filtered and sorted data
        colleges = db.get_colleges(
            filters=filters,
            sort_by=sort_by,
            ascending=(sort_order == "Ascending")
        )

        # Display results
        if colleges:
            # Convert to pandas DataFrame for better display
            df = pd.DataFrame([{
                "Name": c.name,
                "State": c.state,
                "Type": c.type,
                "In-State Tuition": f"${float(c.tuition_in):,.2f}" if c.tuition_in else "N/A",
                "Out-of-State Tuition": f"${float(c.tuition_out):,.2f}" if c.tuition_out else "N/A",
                "Acceptance Rate": f"{float(c.acceptance_rate)*100:.1f}%" if c.acceptance_rate else "N/A",
                "Enrollment": f"{c.enrollment:,}" if c.enrollment else "N/A",
                "Retention Rate": f"{float(c.retention_rate)*100:.1f}%" if c.retention_rate else "N/A",
                "Graduation Rate": f"{float(c.graduation_rate)*100:.1f}%" if c.graduation_rate else "N/A"
            } for c in colleges])

            st.dataframe(df)
            st.write(f"Found {len(colleges)} colleges matching your criteria")

            # Export functionality
            if st.button("Export Results to CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="college_results.csv",
                    mime="text/csv"
                )
        else:
            st.info("No colleges found matching your criteria")

    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    show_college_explorer()