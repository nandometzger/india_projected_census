import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import numpy as np
from matplotlib.colors import LogNorm

def calculate_density_trends():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data", "raw")
    output_dir = os.path.join(project_root, "data", "processed")
    docs_dir = os.path.join(project_root, "docs")
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    print("--- Population Density Trend Analysis (2011-2036) ---")

    # 1. Load Spatial Data & Calculate Area
    geojson_path = os.path.join(data_dir, "india_districts.geojson")
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    gdf = gpd.GeoDataFrame.from_features(data['features'])
    if gdf.crs is None: gdf.set_crs(epsg=4326, inplace=True)
    gdf['area_km2'] = gdf.to_crs(epsg=3857).geometry.area / 1e6

    # 2. Get 2021 District Population Weights Mapping to States
    ipi_path = os.path.join(data_dir, "IPI_District_Data.xlsx")
    xl = pd.ExcelFile(ipi_path)
    labels_df = xl.parse('Label Dictionary')
    
    # Map IDs
    dist_map = labels_df.iloc[1:].set_index('District ID')['Unnamed: 1'].to_dict()
    state_map = labels_df.iloc[1:].set_index('District ID')['Unnamed: 3'].to_dict() # District ID -> State Name
    
    dist_data = xl.parse('Indicator-District Data')
    ind10 = dist_data[dist_data['Indicator ID'] == 10].copy()
    ind10['dist_name'] = ind10['District ID'].map(dist_map)
    ind10['state_name'] = ind10['District ID'].map(state_map)
    ind10['pop_base'] = (ind10['Headcount 2021'] / (ind10['Prevalence 2021'] / 100)).replace([np.inf, -np.inf], np.nan)
    
    weights_df = ind10[['dist_name', 'state_name', 'pop_base']].dropna()
    # Calculate district share within each state
    state_totals = weights_df.groupby('state_name')['pop_base'].transform('sum')
    weights_df['weight'] = weights_df['pop_base'] / state_totals

    # 3. Load State-level Projections
    proj_path = os.path.join(data_dir, "india_projections_2011_2036_total.csv")
    proj_df = pd.read_csv(proj_path, skiprows=1)
    
    # Clean projections
    proj_df = proj_df[proj_df.iloc[:, 1].astype(str).str.strip().str.upper() == 'PERSON']
    target_years = ['2011', '2021', '2025', '2031', '2036']
    
    # Mapping Projection columns (assuming Unnamed: 2 is 2011, sequential years)
    # Based on previous check: 2011 is Unnamed: 2, 2021 is Unnamed: 12, ...
    # 2025 is Unnamed: 16, 2031 is Unnamed: 22, 2036 is Unnamed: 27
    year_map = {'2011': 'Unnamed: 2', '2021': 'Unnamed: 12', '2025': 'Unnamed: 16', '2031': 'Unnamed: 22', '2036': 'Unnamed: 27'}
    
    def normalize(name):
        return str(name).upper().replace(' ', '').replace('-', '').replace('.', '')

    proj_df['state_key'] = proj_df.iloc[:, 0].apply(normalize)
    weights_df['state_key'] = weights_df['state_name'].apply(normalize)

    # 4. Disaggregate
    dist_projections = weights_df.copy()
    for year, col in year_map.items():
        state_vals = proj_df.set_index('state_key')[col].apply(lambda x: float(str(x).replace(',', '')) * 1000 if pd.notna(x) else np.nan)
        dist_projections[f'pop_{year}'] = dist_projections.apply(lambda row: state_vals.get(row['state_key'], np.nan) * row['weight'], axis=1)

    # 5. Join to Geodataframe
    gdf['join_key'] = gdf['shapeName'].apply(normalize)
    dist_projections['join_key'] = dist_projections['dist_name'].apply(normalize)
    
    master = gdf.merge(dist_projections.drop(columns=['state_name', 'state_key']), on='join_key', how='left')

    # Calculate densities
    for year in target_years:
        master[f'density_{year}'] = master[f'pop_{year}'] / master['area_km2']

    # 6. Final Visualization (3x2 Grid)
    fig, axes = plt.subplots(2, 3, figsize=(24, 16), facecolor='#f8f9fa')
    axes = axes.flatten()
    
    vmin, vmax = 100, 20000

    for i, year in enumerate(target_years):
        ax = axes[i]
        master.plot(column=f'density_{year}', ax=ax, cmap='YlGnBu', norm=LogNorm(vmin=vmin, vmax=vmax),
                    legend=True, 
                    legend_kwds={'label': f"Density (people/km²)", 'orientation': "horizontal", 'pad': 0.02, 'shrink': 0.8},
                    edgecolor='#343a40', linewidth=0.03)
        ax.set_title(f"India Population Density: {year}", fontsize=20, fontweight='bold')
        ax.axis('off')

    # Hide extra subplot
    axes[-1].axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(docs_dir, "india_density_trends_2011_2036.png"), dpi=300, bbox_inches='tight')
    
    # Save output
    master.drop(columns=['join_key']).to_json()
    with open(os.path.join(output_dir, "india_density_projections.geojson"), 'w', encoding='utf-8') as f:
        f.write(master.drop(columns=['join_key']).to_json())

    print("Successfully generated 2011-2036 density projections.")

if __name__ == "__main__":
    calculate_density_trends()
