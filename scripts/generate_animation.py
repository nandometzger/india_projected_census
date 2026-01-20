import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import numpy as np
from matplotlib.colors import LogNorm
from PIL import Image

def generate_population_animation():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data", "raw")
    output_dir = os.path.join(project_root, "data", "processed")
    docs_dir = os.path.join(project_root, "docs")
    tmp_frames_dir = os.path.join(project_root, "data", "temp_frames")
    
    if not os.path.exists(tmp_frames_dir): os.makedirs(tmp_frames_dir)

    print("--- Generating Population Density Animation (2011-2036) ---")

    # 1. Load Data (Same logic as dynamics analyzer)
    geojson_path = os.path.join(data_dir, "india_districts.geojson")
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    gdf = gpd.GeoDataFrame.from_features(data['features'])
    if gdf.crs is None: gdf.set_crs(epsg=4326, inplace=True)
    gdf['area_km2'] = gdf.to_crs(epsg=3857).geometry.area / 1e6

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

    proj_path = os.path.join(data_dir, "india_projections_2011_2036_total.csv")
    proj_df = pd.read_csv(proj_path, skiprows=1)
    proj_df = proj_df[proj_df.iloc[:, 1].astype(str).str.strip().str.upper() == 'PERSON']
    year_cols = {str(2011 + i): f'Unnamed: {2+i}' for i in range(26)}
    
    def normalize(name):
        return str(name).upper().replace(' ', '').replace('-', '').replace('.', '')

    proj_df['state_key'] = proj_df.iloc[:, 0].apply(normalize)
    weights_df['state_key'] = weights_df['state_name'].apply(normalize)

    dist_projections = weights_df.copy()
    for year, col in year_cols.items():
        state_vals = proj_df.set_index('state_key')[col].apply(lambda x: float(str(x).replace(',', '')) * 1000 if pd.notna(x) else np.nan)
        dist_projections[f'pop_{year}'] = dist_projections.apply(lambda row: state_vals.get(row['state_key'], np.nan) * row['weight'], axis=1)

    gdf['join_key'] = gdf['shapeName'].apply(normalize)
    dist_projections['join_key'] = dist_projections['dist_name'].apply(normalize)
    master = gdf.merge(dist_projections.drop(columns=['state_key']), on='join_key', how='left')

    # 2. Generate Frames
    frames = []
    years = sorted(year_cols.keys())
    
    # Common scale for all frames
    vmin, vmax = 100, 15000
    
    print(f"Generating {len(years)} frames...")
    for year in years:
        frame_path = os.path.join(tmp_frames_dir, f"frame_{year}.png")
        if not os.path.exists(frame_path):
            master[f'density_{year}'] = master[f'pop_{year}'] / master['area_km2']
            fig, ax = plt.subplots(figsize=(10, 12), facecolor='white')
            master.plot(column=f'density_{year}', ax=ax, cmap='magma', norm=LogNorm(vmin=vmin, vmax=vmax),
                        edgecolor='black', linewidth=0.01)
            
            # Add text annotation for the year
            ax.text(0.05, 0.95, f"Year: {year}", transform=ax.transAxes, fontsize=24, fontweight='bold', verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            ax.set_title("India Population Density Evolution", fontsize=18, pad=10)
            ax.axis('off')
            
            # Add colorbar only to the first frame or manage separately
            # For simplicity in GIF frames, we can skip it or add it to all
            plt.savefig(frame_path, dpi=100, bbox_inches='tight')
            plt.close()
        
        frames.append(Image.open(frame_path))
        print(f"Frame {year} ready.", end='\r')

    # 3. Create GIF
    gif_path = os.path.join(docs_dir, "india_population_evolution.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=200, loop=0)
    print(f"\nSuccess: Animation saved to {gif_path}")

    # Clean up temp frames if desired (optional)
    # import shutil
    # shutil.rmtree(tmp_frames_dir)

if __name__ == "__main__":
    generate_population_animation()
