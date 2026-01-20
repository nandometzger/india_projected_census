import pandas as pd
import os

def sanity_check(path):
    print(f"Detailed Sanity Check for {path}...")
    try:
        xl = pd.ExcelFile(path)
        
        # Load sheets
        labels_df = xl.parse('Label Dictionary')
        dist_data = xl.parse('Indicator-District Data')
        
        # Parse labels more carefully
        # Indicator labels are usually in specific columns. Let's find them.
        # Based on snippet, columns 8-9 might be Indicator labels? (checking names in Labels sheet)
        # Let's print the actual columns of labels_df
        print("Label sheet columns:", labels_df.columns.tolist())
        
        # Looking at columns in Label Dictionary:
        # ['District ID', 'Unnamed: 1', 'State ID', 'Unnamed: 3', 'PC ID', 'Unnamed: 5', 
        #  'Indicator ID', 'Unnamed: 7', 'Category ID', 'Unnamed: 9', 'Indicator Direction', 
        #  'Unnamed: 11', 'Change Availability', 'Unnamed: 13', 'Prevalence Change Category', 'Unnamed: 15']
        
        # Mapping dictionaries
        dist_map = labels_df.iloc[1:].set_index('District ID')['Unnamed: 1'].to_dict()
        indicator_map = labels_df.iloc[1:].set_index('Indicator ID')['Unnamed: 7'].to_dict()
        state_map = labels_df.iloc[1:].set_index('State ID')['Unnamed: 3'].to_dict()
        
        # Clean up maps (remove NaNs)
        dist_map = {k: v for k, v in dist_map.items() if pd.notna(k)}
        indicator_map = {k: v for k, v in indicator_map.items() if pd.notna(k)}
        state_map = {k: v for k, v in state_map.items() if pd.notna(k)}

        print(f"\nExample Indicator ID 1: {indicator_map.get(1, 'Unknown')}")
        
        # Let's merge or map labels to dist_data
        dist_data['District Name'] = dist_data['District ID'].map(dist_map)
        dist_data['Indicator Name'] = dist_data['Indicator ID'].map(indicator_map)
        
        # Select some interesting columns
        cols_to_show = ['District Name', 'Indicator Name', 'Prevalence 2021', 'Headcount 2021']
        available_cols = [c for c in cols_to_show if c in dist_data.columns]
        
        print("\n--- Samples with Labels ---")
        print(dist_data[available_cols].head(20))
        
        # Check Total Headcount for a few major indicators to see if they sum up correctly
        print("\n--- Headcount Sanity Check ---")
        # Sum of headcount for Indicator 1 across all districts
        total_hc_ind1 = dist_data[dist_data['Indicator ID'] == 1]['Headcount 2021'].sum()
        print(f"Total Headcount for Indicator 1 across all districts: {total_hc_ind1:,.0f}")
        
    except Exception as e:
        print(f"Error during sanity check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(project_root, "data", "raw", "IPI_District_Data.xlsx")
    sanity_check(path)
