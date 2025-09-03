import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime as dt
import os
import time
import altair as alt

# Assuming ficture_processing.py and style.py are in the same directory
from ficture_processing import ficture_allocation
from style import apply_styles

st.set_page_config(page_title="File Input", layout="wide")

# Apply the custom styles from the separate file
apply_styles()

@st.cache_data
def load_data(file):
    """
    Loads data from an uploaded CSV or Excel file.
    """
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def main():
    """
    Main function for the Streamlit application UI.
    """
    st.title("Ficture Allocation App")
    
    # --- UI for File Upload ---
    uploaded_file = st.file_uploader("📥 Upload your CSV or Excel file", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if df is not None:
            st.success("✅ File loaded successfully!")
            
            # Place the dataframe preview after the upload success message
            st.write("Preview of the data:")
            st.dataframe(df.head())
            
            # --- User input for column names ---
            st.subheader("⚙️ Map Your Columns")
            st.write("Please provide the exact column names from your file for the allocation logic.")
            
            # Use columns to organize the input fields within the expander
            with st.expander(""):
                # Use st.session_state to persist input values
                if 'col_map' not in st.session_state:
                    st.session_state['col_map'] = {
                        'store': 'STORE',
                        'department': 'DEPARTMENT',
                        'udf': 'UDF-06',
                        'mc_fic': 'MC FIX',
                        'cont_per': 'CONT%',
                        'art': 'ART'
                    }

                col1, col2 = st.columns(2)
                with col1:
                    st.session_state['col_map']['store'] = st.text_input("Store Column Name", value=st.session_state['col_map']['store'])
                    st.session_state['col_map']['department'] = st.text_input("Department Column Name", value=st.session_state['col_map']['department'])
                    st.session_state['col_map']['udf'] = st.text_input("UDF-06 Column Name", value=st.session_state['col_map']['udf'])
                with col2:
                    st.session_state['col_map']['mc_fic'] = st.text_input("MC FIX Column Name", value=st.session_state['col_map']['mc_fic'])
                    st.session_state['col_map']['cont_per'] = st.text_input("CONT% Column Name", value=st.session_state['col_map']['cont_per'])
                    st.session_state['col_map']['art'] = st.text_input("ART Column Name", value=st.session_state['col_map']['art'])

            if st.button("🚀 Process Ficture Allocation"):
                # Pass the column mapping to the processing function
                st.session_state['cols'] = st.session_state['col_map']
                
                # The key change is here: creating the placeholder
                status_placeholder = st.empty()
                
                # Capture the start time
                start_time = dt.now()
                
                # Pass the placeholder and the entire column mapping dictionary
                result_df = ficture_allocation(
                    df, 
                    status_placeholder, 
                    st.session_state['cols']
                )
                
                # Capture the end time and calculate the total duration
                end_time = dt.now()
                total_duration = end_time - start_time
                
                # After the function completes, clear the placeholder and show the completion message
                status_placeholder.empty()
                st.write(f"🎉 Processing completed in: {total_duration}")

                # Use session state to store the processed DataFrame and prevent re-running
                st.session_state['processed_df'] = result_df

    # Display processed data and visualizations if available in session state
    if 'processed_df' in st.session_state:
        result_df = st.session_state['processed_df']
        col_map = st.session_state['cols']
        st.write("📊 Processed Data:")

        # --- Filter section for processed data ---
        with st.expander("🔎 Filter Processed Data"):
            # Get unique values for filters and add a "Show All" option
            stores = ['Show All'] + sorted(list(result_df[col_map['store']].unique()))
            departments = ['Show All'] + sorted(list(result_df[col_map['department']].unique()))
            udfs = ['Show All'] + sorted(list(result_df[col_map['udf']].unique()))

            col1, col2, col3 = st.columns(3)
            selected_store = col1.selectbox("Filter by Store", stores)
            selected_department = col2.selectbox("Filter by Department", departments)
            selected_udf = col3.selectbox("Filter by UDF-06", udfs)
        
        # Apply filters
        filtered_df = result_df.copy()
        if selected_store != 'Show All':
            filtered_df = filtered_df[filtered_df[col_map['store']] == selected_store]
        if selected_department != 'Show All':
            filtered_df = filtered_df[filtered_df[col_map['department']] == selected_department]
        if selected_udf != 'Show All':
            filtered_df = filtered_df[filtered_df[col_map['udf']] == selected_udf]

        st.dataframe(filtered_df)

        # --- Visualization section ---
        st.header("📈 Visualizations")
        with st.expander("View Visualizations"):
            chart1, chart2 = st.columns(2)

            # Chart 1: Total Final Allocation by Store
            with chart1:
                st.subheader("Total Allocation by Store")
                store_allocation = result_df.groupby(col_map['store'])['Final'].sum().reset_index()
                st.bar_chart(store_allocation, x=col_map['store'], y='Final')
            
            # Chart 2: Total Allocation by Pass
            with chart2:
                st.subheader("Allocation Breakdown by Pass")
                pass_allocation = pd.DataFrame({
                    'Pass': ['Pass 1', 'Pass 2', 'Pass 3'],
                    'Allocation': [
                        result_df['Allocate_0'].sum(),
                        result_df['Allocate_1'].sum(),
                        result_df['Allocate_2'].sum()
                    ]
                })

                # Use Altair for more customization
                chart = alt.Chart(pass_allocation).mark_bar().encode(
                    x=alt.X('Pass', sort=None),
                    y=alt.Y('Allocation', title='Total Allocation'),
                    tooltip=['Pass', 'Allocation']
                ).properties(
                    title='Total Allocation by Pass',
                    width=600,
                    height=400
                )

                st.altair_chart(chart, use_container_width=True)

        # Provide download link for the processed data
        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Processed Data as CSV",
            data=csv,
            file_name='processed_ficture_allocation.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()

