# GroundWatch – Data Preprocessing Report

## 1. Overview

The purpose of this stage was to collect, inspect, clean and prepare groundwater-level data for the GroundWatch project. The processed dataset combines historical and recent groundwater observations from the available CGWB Karnataka CSV files.

## 2. Dataset Details

Two datasets were used:

- `gwl_manual_quarterly_cgwb_ka_1991_2020.csv`
- `gwl_manual_quarterly_25.csv`

| Dataset | Records |
|---|---:|
| Historical | 104,781 |
| Recent | 18,686 |
| **Combined** | **123,467** |

The combined dataset contains 24 columns and covers the period from 5 January 1996 to 30 August 2024.

It contains observations from 3,073 unique monitoring locations across 33 districts.

## 3. Data Preprocessing

The following operations were performed:

1. Loaded and inspected both CSV datasets.
2. Checked the column structure, data types and missing values.
3. Combined the historical and recent datasets.
4. Added a `Source` column to identify whether each record came from the historical or recent dataset.
5. Removed records with missing groundwater-level target values.
6. Converted the `Data Acquisition Time` column into datetime format.
7. Converted latitude, longitude and groundwater-level readings into numeric data types.
8. Removed leading and trailing spaces from text fields.
9. Created a `Station_ID` using station name, district and geographical coordinates to distinguish monitoring locations.
10. Preserved the original raw datasets without modifying them.

## 4. Missing Value Analysis

The groundwater-level target column had 165 missing values in the recent dataset and no missing values in the historical dataset. These records were excluded from the combined modelling dataset.

The `RL_MSL` column contained only 393 non-null values in the combined dataset. It was retained rather than removed during preprocessing.

## 5. Preliminary Anomaly Screening

A preliminary screening rule was applied to identify potentially unusual groundwater readings.

Readings below 0 metres or above 100 metres were marked using the `Anomaly_Flag` column.

| Category | Records |
|---|---:|
| Flagged readings | 76 |
| Other readings | 123,391 |
| Total | 123,467 |

The flagged records were retained in the main processed dataset and separately exported for further investigation.

These readings are not confirmed errors. They require further validation before any decision is made to remove or modify them.

## 6. Exploratory Data Analysis

Basic exploratory data analysis was performed to understand the combined dataset.

| Measure | Result |
|---|---:|
| Total records | 123,467 |
| Historical records | 104,781 |
| Recent records | 18,686 |
| Unique monitoring locations | 3,073 |
| Districts | 33 |
| Mean groundwater level | 7.33 m |
| Median groundwater level | 5.70 m |
| Standard deviation | 8.03 m |
| Minimum groundwater level | -1.65 m |
| Maximum groundwater level | 1,374 m |

The mean is higher than the median, indicating that some high readings influence the overall distribution.

## 7. Output Files

The following processed files were generated:

- `data/processed/groundwater_cleaned.csv` – contains all 123,467 records, including the preliminary anomaly flags.
- `data/processed/groundwater_anomalies.csv` – contains the 76 records flagged for further investigation.

The preprocessing notebook is maintained separately under the `notebooks` directory.

## 8. Conclusion

The historical and recent groundwater datasets were combined, inspected and prepared for the next stage of the GroundWatch project.

The resulting dataset contains 123,467 groundwater observations from 3,073 unique monitoring locations across 33 districts. Preliminary suspicious readings have been flagged and preserved for further investigation.

The processed dataset is ready to be handed over to the next team member for modelling and further analysis.