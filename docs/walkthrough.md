# Indian Census Data Acquisition Walkthrough

This document summarizes the research and data acquisition process for the Indian Census.

## Research Findings
- **Latest Census**: Conducted in **2011** (15th decennial census).
- **Next Census**: Scheduled for **2027**. (Postponed from 2021 due to COVID-19).
- **Extrapolations**: Official population projections are available for **2011-2036** from the "Report of the Technical Group on Population Projections July 2020", published by the National Commission on Population.


## Data Downloaded
The following files were downloaded to `c:\Users\nando\Downloads\popcornoutputs\india_census\`:

1.  **[india_pca_2011_total.csv](file:///c:/Users/nando/Downloads/popcornoutputs/india_census/india_pca_2011_total.csv)**: Primary Census Abstract 2011 (District-level statistics).
2.  **[india_pca_colnames.csv](file:///c:/Users/nando/Downloads/popcornoutputs/india_census/india_pca_colnames.csv)**: Column mappings for PCA data.
3.  **[india_projections_2011_2036_total.csv](file:///c:/Users/nando/Downloads/popcornoutputs/india_census/india_projections_2011_2036_total.csv)**: Year-wise population projections for India and States (2011-2036).
4.  **[india_projections_2011_2036_age_sex.csv](file:///c:/Users/nando/Downloads/popcornoutputs/india_census/india_projections_2011_2036_age_sex.csv)**: Age-group and sex-wise population projections (2011-2036).
5.  **[IPI_District_Data.xlsx](file:///c:/Users/nando/Downloads/popcornoutputs/india_census/IPI_District_Data.xlsx)**: Granular district-level indicators (122 indicators for 2016 and 2021).
6.  **[ind_pop_2025_100m_constrained.tif](file:///c:/Users/nando/Downloads/popcornoutputs/india_census/ind_pop_2025_100m_constrained.tif)**: 100m gridded population counts for 2025.

## Verification
- Verified PCA CSV files contain expected district-level demographics.
- Verified Projection CSV files contain year-wise estimates for India and States.
- **Granular Verification**: Checked IPI Excel structure; confirmed `Indicator-District Data` sheet contains mapped names (e.g., "Alluri Sitharama Raju") and 2021 headcount figures.
- **Gridded Verification**: Confirmed 750MB GeoTIFF download complete for 2025 distribution.
