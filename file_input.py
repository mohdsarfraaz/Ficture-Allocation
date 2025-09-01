import pandas as pd
import numpy as np
from datetime import datetime as dt
import streamlit as st
import os
from ficture_processing import ficture_allocation

st.set_page_config(page_title="File Input", layout="wide")
@st.cache_data
def load_data(file):
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
    st.title("File Input for Ficture Allocation")
    uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=['csv', 'xlsx', 'xls'])
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if df is not None:
            st.success("File loaded successfully!")
            st.write("Preview of the data:")
            st.dataframe(df.head())
            
            if st.button("Process Ficture Allocation"):
                start_time = dt.now()
                result_df = ficture_allocation(df)
                end_time = dt.now()
                st.write(f"Processing completed in: {end_time - start_time}")
                st.write("Processed Data:")
                st.dataframe(result_df)
                
                # Provide download link for the processed data
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Processed Data as CSV",
                    data=csv,
                    file_name='processed_ficture_allocation.csv',
                    mime='text/csv',
                )

if __name__ == "__main__":
    main()


