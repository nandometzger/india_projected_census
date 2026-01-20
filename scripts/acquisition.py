import os
import requests
import pandas as pd

def download_file(url, target_path):
    print(f"Downloading {url} to {target_path}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded to {target_path}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def main():
    # Use relative path to data/raw
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "data", "raw")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. 2011 Primary Census Abstract (PCA) - India and States
    # Using Pigshell's verified GitHub links
    pca_total_url = "https://raw.githubusercontent.com/pigshell/india-census-2011/master/pca-total.csv"
    pca_path = os.path.join(output_dir, "india_pca_2011_total.csv")
    download_file(pca_total_url, pca_path)
    
    pca_colnames_url = "https://raw.githubusercontent.com/pigshell/india-census-2011/master/pca-colnames.csv"
    colnames_path = os.path.join(output_dir, "india_pca_colnames.csv")
    download_file(pca_colnames_url, colnames_path)

    # 2. Population Projections 2011-2036 
    # Google Sheets mirrors (CSV exports)
    base_gs_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vResje75KBrkVLfyH65aujGBZiTm0MzAyr2xGXXA2qx7rv4bt9FiFardJnf0yRd3CfYi3ufRJ_rilAk/pub?output=csv"
    
    # Total Population by Sex (gid=1454217272)
    proj_total_url = f"{base_gs_url}&gid=1454217272"
    proj_total_path = os.path.join(output_dir, "india_projections_2011_2036_total.csv")
    download_file(proj_total_url, proj_total_path)

    # Age-wise Population (gid=1827216026)
    proj_age_url = f"{base_gs_url}&gid=1827216026"
    proj_age_path = os.path.join(output_dir, "india_projections_2011_2036_age_sex.csv")
    download_file(proj_age_url, proj_age_path)

    # 3. Granular IPI District Data (Harvard Dataverse)
    # fileId: 11975380 (IPI_District_Data.xlsx)
    ipi_dist_url = "https://dataverse.harvard.edu/api/access/datafile/11975380"
    ipi_dist_path = os.path.join(output_dir, "IPI_District_Data.xlsx")
    download_file(ipi_dist_url, ipi_dist_path)

    # 4. WorldPop India 2025 Total Population (100m Constrained)
    wp_2025_url = "https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/2025/IND/v1/100m/constrained/ind_pop_2025_CN_100m_R2025A_v1.tif"
    wp_2025_path = os.path.join(output_dir, "ind_pop_2025_100m_constrained.tif")
    download_file(wp_2025_url, wp_2025_path)

    # 5. Spatial Boundaries (Districts - GeoJSON from HDX/geoBoundaries)
    # ADM2 corresponds to Districts
    spatial_url = "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/IND/ADM2/geoBoundaries-IND-ADM2.geojson"
    spatial_path = os.path.join(output_dir, "india_districts.geojson")
    download_file(spatial_url, spatial_path)

    print("\nDownload process complete.")

if __name__ == "__main__":
    main()
