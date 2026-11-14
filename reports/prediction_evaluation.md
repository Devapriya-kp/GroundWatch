
# GroundWatch - Prediction Model Evaluation

## 1. Objective

To evaluate the groundwater prediction models and select
the best-performing regression model.

## 2. Models Evaluated

- Baseline
- Linear Regression
- Decision Tree Regressor
- Random Forest Regressor

## 3. Model Comparison

| Model             |     MAE |     RMSE |         R2 |
|:------------------|--------:|---------:|-----------:|
| Random Forest     | 1.89051 |  9.55501 |  0.21348   |
| Decision Tree     | 1.98615 |  9.63151 |  0.200836  |
| Linear Regression | 2.05511 | 10.866   | -0.0171475 |
| Baseline          | 2.41696 | 13.3374  | -0.532452  |

## 4. Selected Model

**Random Forest**

## 5. Evaluation Metrics

- MAE: 1.8905
- RMSE: 9.5550
- R²: 0.2135

## 6. Evaluation Observations

Random Forest achieved the lowest RMSE among the four
evaluated approaches.

The model was also evaluated separately on known and
unseen stations.

- Known stations: 21,645 records
- Unseen stations: 1,138 records

## 7. Limitations

The R² value indicates modest explanatory performance.
Some large prediction errors were observed.

An extreme groundwater reading of 1374 metres was
identified in the test data. It was retained in the
evaluation and its effect should be considered when
interpreting the results.

## 8. Conclusion

Random Forest was selected as the best-performing model
among the tested approaches. Further validation and
data-quality investigation are necessary before
operational use.
