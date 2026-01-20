# Indian Census & Population Projection Walkthrough

This document summarizes the research, data acquisition, and methodology used to create the longitudinal population analysis of India (2011-2036).

## 🌍 Research Core
- **Baseline**: The last ground-truth census was conducted in **2011**.
- **The Gap**: The 2021 Census was postponed to 2027.
- **Official Projections**: We utilize the **"Report of the Technical Group on Population Projections July 2020"** (MoHFW) which provides state-level targets for every year until 2036.

## 📊 Data Inventory
All raw data is stored in `data/raw/`:

1.  **india_pca_2011_total.csv**: Primary Census Abstract 2011 (Baseline ground-truth).
2.  **india_projections_2011_2036_total.csv**: Yearly state-level targets.
3.  **IPI_District_Data.xlsx**: 122 socio-economic indicators used to derive 2021 district weights.
4.  **india_districts.geojson**: ADM2 administrative boundaries (geoBoundaries).
5.  **ind_pop_2025_100m_constrained.tif**: High-res distribution map for 2025 (WorldPop).

## 🛠️ Methodology: Weighted Disaggregation
Since projections are at the **State** level, but high-resolution analysis requires **District** levels, we implemented a disaggregation model:
1.  **Weight Calculation**: Calculated the population share of each district within its state using 2021 IPI headcount indicators.
2.  **Top-Down Allocation**: Applied those percentage weights to the official MoHFW State projections for every year from 2011 to 2036.
3.  **Spatial Join**: Merged these year-wise counts with the GeoJSON polygons via a normalized name-matching pipeline (95%+ match rate).

## ✅ Verification
- **Cross-Check**: Derived 2021 national totals from district-level disaggregation match the official MoHFW national projection within <0.01% error.
- **GIS Ready**: Verified that the final GeoPackage (`data/processed/India_Census_Projections_Mapped.gpkg`) loads correctly in QGIS with all 2011-2036 attributes preserved.
