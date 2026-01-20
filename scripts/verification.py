import pandas as pd
import os

def check_discrepancy():
    print("--- Official vs IPI Population Comparison 2021 ---")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ipi_path = os.path.join(project_root, "data", "raw", "IPI_District_Data.xlsx")
    proj_path = os.path.join(project_root, "data", "raw", "india_projections_2011_2036_total.csv")
    
    try:
        # Load Projections
        proj_df = pd.read_csv(proj_path, skiprows=1)
        
        # Row 1 (India, Person)
        india_row = proj_df[proj_df.iloc[:, 0].astype(str).str.strip().str.upper() == 'INDIA'].head(1)
        
        # 2011 is Unnamed: 2. 2021 is Unnamed: 12.
        # Let's verify by printing the slice
        cols = india_row.iloc[0, 2:13] # from 2011 to 2021
        print("\nProjection Sequence (2011 to 2021):")
        print(cols.values)
        
        official_2021_val = float(india_row['Unnamed: 12'].values[0]) * 1000
        print(f"\nOfficial Total-India Projection 2021 (from index 12): {official_2021_val:,.0f}")

        # Load IPI Totals
        xl = pd.ExcelFile(ipi_path)
        india_totals = xl.parse('Indicator-Specific Data')
        
        # indicator 10: Health Insurance [Any]
        # This is a good proxy because insurance is calculated against the whole population headcount.
        row_ind10 = india_totals[india_totals['Indicator ID'] == 10].iloc[0]
        prev_10 = row_ind10['All India Prevalence 2021'] 
        hc_10 = row_ind10['All India Headcount 2021'] 
        derived_pop = (hc_10 / (prev_10 / 100))
        
        print(f"IPI Derived Total Population: {derived_pop:,.0f}")

        # Comparison
        diff = derived_pop - official_2021_val
        percent_diff = (diff / official_2021_val) * 100
        
        print(f"\n--- Final Result ---")
        print(f"Official Projection: {official_2021_val:,.0f}")
        print(f"IPI Derived Pop:     {derived_pop:,.0f}")
        print(f"Percentage Gap:      {percent_diff:.2f}%")
        
        if abs(percent_diff) < 1:
            print("\nCONCLUSION: THE DATA IS EXTREMELY ACCURATE. (Gap < 1%)")
        elif abs(percent_diff) < 5:
            print("\nCONCLUSION: BALLPARK MATCH. (Gap < 5%)")
        else:
            print("\nCONCLUSION: DATA DISCREPANCY DETECTED.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_discrepancy()
