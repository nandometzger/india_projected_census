import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import numpy as np
from matplotlib.colors import LogNorm

def generate_advanced_dynamics():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data", "raw")
    output_dir = os.path.join(project_root, "data", "processed")
    docs_dir = os.path.join(project_root, "docs")
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    print("--- Advanced Population Dynamics & Growth Analysis ---")

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
    
    dist_map = labels_df.iloc[1:].set_index('District ID')['Unnamed: 1'].to_dict()
    state_map = labels_df.iloc[1:].set_index('District ID')['Unnamed: 3'].to_dict()
    
    dist_data = xl.parse('Indicator-District Data')
    ind10 = dist_data[dist_data['Indicator ID'] == 10].copy()
    ind10['dist_name'] = ind10['District ID'].map(dist_map)
    ind10['state_name'] = ind10['District ID'].map(state_map)
    ind10['pop_base'] = (ind10['Headcount 2021'] / (ind10['Prevalence 2021'] / 100)).replace([np.inf, -np.inf], np.nan)
    
    weights_df = ind10[['dist_name', 'state_name', 'pop_base']].dropna()
    state_totals = weights_df.groupby('state_name')['pop_base'].transform('sum')
    weights_df['weight'] = weights_df['pop_base'] / state_totals

    # 3. Load State-level Projections
    proj_path = os.path.join(data_dir, "india_projections_2011_2036_total.csv")
    proj_df = pd.read_csv(proj_path, skiprows=1)
    proj_df = proj_df[proj_df.iloc[:, 1].astype(str).str.strip().str.upper() == 'PERSON']
    
    # Yearly columns range: Unnamed: 2 (2011) to Unnamed: 27 (2036)
    year_cols = {str(2011 + i): f'Unnamed: {2+i}' for i in range(26)}
    
    def normalize(name):
        return str(name).upper().replace(' ', '').replace('-', '').replace('.', '')

    proj_df['state_key'] = proj_df.iloc[:, 0].apply(normalize)
    weights_df['state_key'] = weights_df['state_name'].apply(normalize)

    # 4. Disaggregate for all years to enable line plots
    dist_projections = weights_df.copy()
    for year, col in year_cols.items():
        state_vals = proj_df.set_index('state_key')[col].apply(lambda x: float(str(x).replace(',', '')) * 1000 if pd.notna(x) else np.nan)
        dist_projections[f'pop_{year}'] = dist_projections.apply(lambda row: state_vals.get(row['state_key'], np.nan) * row['weight'], axis=1)

    # 5. Join to Geodataframe
    gdf['join_key'] = gdf['shapeName'].apply(normalize)
    dist_projections['join_key'] = dist_projections['dist_name'].apply(normalize)
    master = gdf.merge(dist_projections.drop(columns=['state_key']), on='join_key', how='left')

    # 6. Specialized Visualizations

    # --- VIZ 1: SINGLE TEASER MAP (2025 Density) ---
    print("Generating Teaser Map (2025)...")
    master['density_2025'] = master['pop_2025'] / master['area_km2']
    fig, ax = plt.subplots(figsize=(15, 18), facecolor='white')
    master.plot(column='density_2025', ax=ax, cmap='magma', norm=LogNorm(vmin=100, vmax=15000),
                legend=True, 
                legend_kwds={'label': "Projected People per km²", 'orientation': "horizontal", 'pad': 0.02, 'shrink': 0.6},
                edgecolor='black', linewidth=0.3)
    ax.set_title("India Population Density Projection: 2025", fontsize=28, fontweight='bold', pad=30)
    ax.axis('off')
    plt.savefig(os.path.join(docs_dir, "teaser_density_2025.png"), dpi=300, bbox_inches='tight')

    # --- VIZ 2: GROWTH TREND LINE PLOT (National) ---
    print("Generating National Trend Line...")
    years = [int(y) for y in year_cols.keys()]
    national_pops = [dist_projections[f'pop_{y}'].sum() / 1e9 for y in year_cols.keys()] # In Billions

    plt.figure(figsize=(12, 7), facecolor='#f8f9fa')
    plt.plot(years, national_pops, marker='o', color='#d63031', linewidth=3, markersize=8)
    plt.fill_between(years, national_pops, color='#d63031', alpha=0.1)
    plt.title("Total Population Projection of India (2011 - 2036)", fontsize=20, fontweight='bold', pad=20)
    plt.xlabel("Year", fontsize=14)
    plt.ylabel("Population (Billions)", fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(np.arange(2011, 2037, 5))
    plt.savefig(os.path.join(docs_dir, "national_growth_trend.png"), dpi=300, bbox_inches='tight')

    # --- VIZ 3: GROWTH MAPS (Dynamics) ---
    print("Generating Growth Dynamics Map...")
    master['growth_rate'] = ((master['pop_2036'] / master['pop_2011'])**(1/25) - 1) * 100
    fig, ax = plt.subplots(figsize=(15, 15), facecolor='#f8f9fa')
    master.plot(column='growth_rate', ax=ax, cmap='RdYlGn_r', vmin=-0.5, vmax=2.5,
                legend=True, legend_kwds={'label': "Annualized Growth Rate (%)", 'orientation': "horizontal", 'pad': 0.05, 'shrink': 0.6},
                edgecolor='grey', linewidth=0.1)
    ax.set_title("Spatial Dynamics: Total Growth Rate (2011 - 2036)", fontsize=22, fontweight='bold', pad=20)
    ax.axis('off')
    plt.savefig(os.path.join(docs_dir, "spatial_growth_dynamics.png"), dpi=300, bbox_inches='tight')

    # 7. Export to GeoPackage for QGIS
    print("Exporting GeoPackage for QGIS...")
    # Calculate more densities for the GeoPackage
    for y in ['2011', '2021', '2031', '2036']:
        master[f'density_{y}'] = master[f'pop_{y}'] / master['area_km2']

    # Final Column Selection & Renaming for QGIS
    # Re-fetch state names as they were dropped in the merge earlier or were part of dist_projections
    # Let's ensure state_name is preserved. 
    # Actually, dist_projections has 'state_name'. Let's check the merge again.
    # Current merge: master = gdf.merge(dist_projections.drop(columns=['state_name', 'state_key']), on='join_key', how='left')
    # Let's fix that merge to keep state_name.

    # Save final results as GeoJSON (Existing)
    with open(os.path.join(output_dir, "india_comprehensive_projections.geojson"), 'w', encoding='utf-8') as f:
        f.write(master.drop(columns=['join_key']).to_json())

    # Export to GPKG using pyogrio
    gpkg_path = os.path.join(output_dir, "India_Census_Projections_Mapped.gpkg")
    try:
        master.drop(columns=['join_key']).to_file(gpkg_path, driver="GPKG", engine="pyogrio")
        print(f"Success: GeoPackage saved to {gpkg_path}")
    except Exception as e:
        print(f"Warning: GeoPackage export failed: {e}")

    print("Success: Advanced Dynamics and Trends generated.")

if __name__ == "__main__":
    generate_advanced_dynamics()
