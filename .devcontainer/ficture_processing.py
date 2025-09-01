import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time

def ficture_allocation(df, status_placeholder, col_map):
    """
    Performs the fixture allocation process and updates a Streamlit UI element
    with the current progress and elapsed time.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        status_placeholder (streamlit.delta_generator.DeltaGenerator):
            A placeholder to update the UI with processing status.
        col_map (dict): A dictionary mapping generic column names to user-defined names.
    """
    start_time = datetime.now()
    
    # Assign column names from the map for easier use
    store_name = col_map['store']
    department = col_map['department']
    udf = col_map['udf']
    mc_fic = col_map['mc_fic']
    cont_per = col_map['cont_per']
    art = col_map['art']

    df_1 = df.copy() # Work on a copy to preserve original data

    # --- 🎯 Step 2: Initialize Data Structures for Allocation Logic ---
    fict_bal_dict = {}
    fict_req_dict = {}

    passes = 3 

    for i in range(passes):
        df_1[f"Allocate_{i}"] = np.zeros(len(df_1))
        df_1[f"MC_BAl_{i}"] = np.zeros(len(df_1))
        df_1[f"FIC_REQ_{i}"] = np.zeros(len(df_1))
        
    df_1['rest_per'] = np.zeros(len(df_1))

    # --- 🎯 Step 3 & 4: Group and Process Data (with new outer loop structure) ---
    for i in range(passes): # i will be 0, 1, 2
        # Update the UI with the current pass and elapsed time
        elapsed_time = datetime.now() - start_time
        elapsed_time = str(elapsed_time).split('.')[0] # Format to HH:MM:SS   
        status_placeholder.write(f"Processing Pass {i+1} of {passes}... Elapsed Time: {elapsed_time}")
        
        # A small delay to make the time update visible in the UI
        time.sleep(1)

        grouped_data = df_1.groupby([store_name, department, udf])

        for (store, dep, disp), group in grouped_data:
            mc_fic_val = group[mc_fic].iloc[0]

            if i <= 1:
                sorted_group = group.sort_values(cont_per, ascending=False).copy()
            else:
                sorted_group = group.sort_values(f"FIC_REQ_{i-1}", ascending=False).copy()
            
            original_indices = sorted_group.index.to_numpy()

            initial_req_fic_group = sorted_group[cont_per] * sorted_group[mc_fic]
            
            reverse_cumsum = sorted_group[cont_per][::-1].cumsum()[::-1]
            rest_per_group = reverse_cumsum.shift(-1).fillna(0.0)
            
            df_1.loc[original_indices, 'rest_per'] = rest_per_group.values

            mc_bal = fict_bal_dict.get((store, dep, disp), mc_fic_val)

            for j, (original_idx, row_data) in enumerate(sorted_group.iterrows()):
                art_key = (store, dep, disp, row_data[art])
                fic_req = fict_req_dict.get(art_key, initial_req_fic_group.loc[original_idx])
                
                if j + 1 < len(sorted_group):
                    next_idx = sorted_group.index[j + 1]
                    next_fic_req = fict_req_dict.get(
                        (store, dep, disp, sorted_group.loc[next_idx, art]),
                        initial_req_fic_group.loc[next_idx]
                    )
                else:
                    next_fic_req = 0

                allocate = 0 
                if i == 0:
                    if mc_bal >= 1 and fic_req > 0.4:
                        allocate = 1
                elif i == 1:
                    if mc_bal > fic_req and rest_per_group.loc[original_idx] >= 0.1:
                        allocate = int(np.round(fic_req))
                elif i == 2:
                    if fic_req > 0 and mc_bal > 0:
                        allocate = int(np.round(mc_bal))

                mc_bal = np.maximum(mc_bal - allocate, 0)
                fic_req = np.maximum(fic_req - allocate, 0)

                fict_req_dict[art_key] = fic_req
                df_1.loc[original_idx, f"Allocate_{i}"] = allocate
            
            fict_bal_dict[(store, dep, disp)] = mc_bal

    df_1["Final"] = sum(df_1[f"Allocate_{i}"] for i in range(passes))
    
    return df_1
