import json
import pandas as pd
import os

def compare_districts():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    geojson_path = os.path.join(project_root, "data", "raw", "india_districts.geojson")
    ipi_path = os.path.join(project_root, "data", "raw", "IPI_District_Data.xlsx")
    
    if not os.path.exists(geojson_path):
        print("GeoJSON not found yet.")
        return

    print("Loading labels from IPI Excel...")
    xl = pd.ExcelFile(ipi_path)
    labels_df = xl.parse('Label Dictionary')
    ipi_districts = labels_df.iloc[1:][['Unnamed: 1']].dropna()
    ipi_set = set(ipi_districts['Unnamed: 1'].str.upper().str.strip())
    print(f"IPI Districts count: {len(ipi_set)}")

    print("Loading GeoJSON...")
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    geo_districts = []
    for feature in data['features']:
        # geoBoundaries usually has 'shapeName' or 'ADM2_EN'
        props = feature['properties']
        name = props.get('shapeName') or props.get('shapeName') or props.get('ADM2_EN') or list(props.values())[0]
        geo_districts.append(str(name).upper().strip())
    
    geo_set = set(geo_districts)
    print(f"GeoJSON Districts count: {len(geo_set)}")
    
    common = ipi_set.intersection(geo_set)
    print(f"Exact Matches: {len(common)}")
    
    missing_in_geo = ipi_set - geo_set
    print(f"\nMissing in GeoJSON (First 10): {sorted(list(missing_in_geo))[:10]}")
    
    missing_in_ipi = geo_set - ipi_set
    print(f"Missing in IPI (First 10): {sorted(list(missing_in_ipi))[:10]}")

if __name__ == "__main__":
    compare_districts()
