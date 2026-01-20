import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import json

def merge_and_visualize():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data", "raw")
    output_dir = os.path.join(project_root, "data", "processed")
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    print("--- Joining Spatial and Statistical Data ---")

    # 1. Load IPI Statistical Data
    ipi_path = os.path.join(data_dir, "IPI_District_Data.xlsx")
    xl = pd.ExcelFile(ipi_path)
    labels_df = xl.parse('Label Dictionary')
    
    dist_map = labels_df.iloc[1:].set_index('District ID')['Unnamed: 1'].to_dict()
    dist_map = {k: str(v).strip() for k, v in dist_map.items() if pd.notna(k)}

    indicator_id = 1
    indicator_name = "Population with BPL cards (Prevalence %)"
    
    dist_data = xl.parse('Indicator-District Data')
    indicator_df = dist_data[dist_data['Indicator ID'] == indicator_id].copy()
    indicator_df['District Name'] = indicator_df['District ID'].map(dist_map)
    stats_df = indicator_df[['District Name', 'Prevalence 2021', 'Headcount 2021']].dropna(subset=['District Name'])

    # 2. Load GeoJSON manually to bypass Fiona error
    geojson_path = os.path.join(data_dir, "india_districts.geojson")
    print(f"Loading GeoJSON from {geojson_path}...")
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    gdf = gpd.GeoDataFrame.from_features(data['features'])
    # Ensure CRS is set (usually WGS84 for GeoJSON)
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    
    # 3. Join
    def normalize(name):
        return str(name).upper().replace(' ', '').replace('-', '').replace('.', '')

    stats_df['join_key'] = stats_df['District Name'].apply(normalize)
    gdf['join_key'] = gdf['shapeName'].apply(normalize)

    merged = gdf.merge(stats_df, on='join_key', how='left')
    match_count = merged['Prevalence 2021'].notna().sum()
    print(f"Matched {match_count} units.")

    # 4. Visualization
    print("Generating Choropleth Map...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 15), facecolor='#f8f9fa')
    
    # Plot missing areas
    gdf.plot(ax=ax, color='#e9ecef', edgecolor='#ced4da', linewidth=0.3)
    
    # Plot the choropleth
    merged.plot(column='Prevalence 2021', 
                ax=ax, 
                legend=True,
                cmap='Spectral_r', 
                legend_kwds={'label': f"{indicator_name} (2021)",
                            'orientation': "horizontal",
                            'pad': 0.05,
                            'shrink': 0.6},
                edgecolor='#495057',
                linewidth=0.1)

    ax.set_title(f"India: {indicator_name}", fontsize=24, fontweight='bold', pad=30, color='#212529')
    ax.annotate('Data Source: India Policy Insights (Harvard/NITI Aayog) | Spatial: geoBoundaries', 
                xy=(0.5, 0.02), xycoords='figure fraction', ha='center', fontsize=10, color='#6c757d')
    ax.axis('off')

    # Save outputs
    map_output = os.path.join(project_root, "docs", "india_bpl_choropleth.png")
    plt.savefig(map_output, dpi=300, bbox_inches='tight')
    print(f"Choropleth saved to {map_output}")
    
    # Save processed data
    merged_output = os.path.join(output_dir, "india_districts_with_stats.geojson")
    # Convert back to JSON string to save, bypassing Fiona writing for now
    json_data = merged.drop(columns=['join_key']).to_json()
    with open(merged_output, 'w', encoding='utf-8') as f:
        f.write(json_data)
    print(f"Unified GeoJSON saved to {merged_output}")

if __name__ == "__main__":
    merge_and_visualize()
