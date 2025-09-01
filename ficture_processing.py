import pandas as pd
import numpy as np

def ficture_allocation(df):
        
    df_1 = df.copy() # Work on a copy to preserve original data
    # --- 🎯 Step 2: Initialize Data Structures for Allocation Logic ---
    # Dictionaries to hold the remaining balances and requests
    fict_bal_dict = {}
    fict_req_dict = {}

    # Set the number of allocation passes
    passes = 3 # As specified by user for outer loop

    # Pre-allocate numpy arrays to hold results for final assignment
    for i in range(passes):
        df_1[f"Allocate_{i}"] = np.zeros(len(df_1))
        df_1[f"MC_BAl_{i}"] = np.zeros(len(df_1)) # To store mc_bal at the end of each pass for each row
        df_1[f"FIC_REQ_{i}"] = np.zeros(len(df_1)) # To store fic_req at the end of each pass for each row
    # Initialize 'rest_per' column
    df_1['rest_per'] = np.zeros(len(df_1))

    # --- 🎯 Step 3 & 4: Group and Process Data (with new outer loop structure) ---
    # Outer loop for allocation passes as per user's new logic
    for i in range(passes): # i will be 0, 1, 2
        print(f"Starting Pass {i}") # Added print statement for clarity

        # Group data within each pass as per user's new logic
        grouped_data = df_1.groupby(['STORE', 'DEPARTMENT', 'UDF-06'])

        for (store, dep, disp), group in grouped_data:
            mc_fic = group['MC FIX'].iloc[0] # Max fixture count for the department

            # Sort the group by 'CONT%' in descending order
            if i <=1:
                sorted_group = group.sort_values('CONT%', ascending=False).copy()
                original_indices = sorted_group.index.to_numpy()
            else:
                sorted_group = group.sort_values(f"FIC_REQ_{i-1}", ascending=False).copy()
                original_indices = sorted_group.index.to_numpy()            

            # Calculate initial required fixtures for the current sorted group
            initial_req_fic_group = sorted_group['CONT%'] * sorted_group['MC FIX']
            
            # --- MODIFICATION START: Corrected rest_per_group calculation ---
            # Calculate reverse cumulative sum of CONT% (sum of current row and all following rows)
            # We reverse the series, calculate the cumulative sum, and then reverse it back.
            reverse_cumsum = sorted_group['CONT%'][::-1].cumsum()[::-1]

            # To get the sum of *only* the following rows (excluding the current one),
            # we shift these reverse cumulative sum values UP by one position.
            # Any resulting NaN at the end (for the last row) are filled with 0.0.
            rest_per_group = reverse_cumsum.shift(-1).fillna(0.0)
            # --- MODIFICATION END ---

            # Store rest_per_group into the DataFrame using original indices
            df.loc[original_indices, 'rest_per'] = rest_per_group.values

            # Get the current balance for this group from the dictionary.
            # If not present (first time for this group), use max_fic.
            mc_bal = fict_bal_dict.get((store, dep, disp), mc_fic)

            # Loop through each row in the sorted group to apply allocation logic
            # Using iterrows to get both index (for df.loc) and row data
            for j, (original_idx, row_data) in enumerate(sorted_group.iterrows()):
                art_key = (store, dep, disp, row_data['ART'])
                
                # Get the remaining required fixtures for this item
                # If not present, use the initial calculated value for this specific item in this group
                fic_req = fict_req_dict.get(art_key, initial_req_fic_group.loc[original_idx])
                initial_fic_req_value = initial_req_fic_group.loc[original_idx]
                rest = rest_per_group.loc[original_idx] # Get rest percentage for this specific item
                allocate = 0 # Initialize allocation for the current item in this pass

                # 👀 Lookahead: get next row's fic_req (if exists)
                if j + 1 < len(sorted_group):
                    next_idx = sorted_group.index[j + 1]
                    next_fic_req = fict_req_dict.get(
                        (store, dep, disp, sorted_group.loc[next_idx, 'ART']),
                        initial_req_fic_group.loc[next_idx]
                    )
                else:
                    next_fic_req = 0

                # Apply the new allocation rules based on the pass number (i)
                if i == 0: # This corresponds to user's "loop 1"
                    # Rule: if mc_bal > 0 and req_fic > 0.4 then allocate 1
                    if mc_bal >= 1 and fic_req > 0.4:
                        allocate = 1
                    else:
                        allocate = 0
                elif i == 1: # This corresponds to user's "loop 2"
                    # Rule: if mc_bal > req_fic and rest is >= 0.1 then allocate round(req_fic)
                    if mc_bal > fic_req and rest >= 0.1:
                        allocate = int(np.round(fic_req))
                    else:
                        # If conditions for loop 2 are not met, allocate 0 for this pass/item
                        allocate = 0
                elif i == 2: # This corresponds to user's "last loop" (Loop 3)
                    # Rule: if rest < 0.1 and req_fic > 0 and mc_bal > 0 then allocate mc_bal
                    
                    if fic_req >0 and mc_bal > 0:
                        allocate = int(np.round(mc_bal)) # User said "allocate the mc_bal"
                    else:
                        # If conditions for loop 3 are not met, allocate 0 for this pass/item
                        allocate = 0
                
                # Ensure allocate does not exceed remaining required fixtures or balance, and is non-negative
                # This clamping is still essential regardless of the allocation rule applied
    #            allocate = min(allocate, int(fic_req)) # Clamp by fic_req first
    #            allocate = min(allocate, int(mc_bal)) # Then clamp by mc_bal
    #            allocate = max(0, allocate) # Allocation cannot be negative

                # Update remaining balance and required fixtures
                mc_bal = np.maximum(mc_bal - allocate, 0)
                fic_req = np.maximum(fic_req - allocate, 0)

                # Store the updated required fixtures for the next iteration/pass
                fict_req_dict[art_key] = fic_req

                # Store results directly back to the main DataFrame using the original index
                df_1.loc[original_idx, f"Allocate_{i}"] = allocate
                #df_1.loc[original_idx, f"MC_BAl_{i}"] = mc_bal # Store the remaining balance of the group after this allocation
                #df_1.loc[original_idx, f"FIC_REQ_{i}"] = fic_req # Store the remaining required fixtures for this item

            # Update the overall balance for the next pass
            fict_bal_dict[(store, dep, disp)] = mc_bal


    # --- 🎯 Step 6: Final Assignment and Calculations ---
    # Calculate the final total allocation per row
    df_1["Final"] = sum(df_1[f"Allocate_{i}"] for i in range(passes))

    
    return df_1