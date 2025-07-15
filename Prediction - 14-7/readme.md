

# Traffic Flow Prediction Using Time-Series Modeling

<img width="440" height="336" alt="Junction Highlighting - Labelled" src="https://github.com/user-attachments/assets/24ad1ac6-06ff-4635-8b01-ee17a34f71b0" />


## Objective



Predict the **FP_D_Count** (vehicle flow) for a **target junction** (e.g., FP D) at time `t` using historical traffic data from 10 monitored junctions.



---



## Junctions in Dataset



The dataset includes time-series data from the following 10 traffic junctions:



* FP A

* FP B

* FP C

* FP D

* Anand Rao JNC

* Race Course JNC

* Palace Rd JNC

* KG Road

* District Office

* KR Circle



Each junction has 3 metrics:



* speed

* count

* queuepct



---



## Target Column



The target variable for all prediction tasks is:



**FP_D_Count** (vehicle count at junction FP D)



---



## Evaluation Metrics



Models will be evaluated using:



* RMSE (Root Mean Squared Error)

* MAE (Mean Absolute Error)

* MAPE (Mean Absolute Percentage Error)

* R² Score (Coefficient of Determination)



---



## Models Compared



* SVM (Support Vector Machine)

* Random Forest Regressor

* XGBRegressor

* RNN (Recurrent Neural Network)

* LSTM (Long Short-Term Memory)

* GRU (Gated Recurrent Unit)

* Transformer (for time-series forecasting)



---



## Dataset Variants



### Variant 1: Plain Dataset



Current values of all 3 metrics from all 10 junctions

**Total columns**: 10 × 3 = 30



### Variant 2: Target Column Lagged



Plain Dataset + `n` lagged values of FP_D_Count only

**Total columns**: 30 + n



### Variant 3: Target Junction Metrics Lagged



Plain Dataset + lagged values of all 3 metrics (speed, count, queuepct) for FP D only

**Total columns**: 30 + 3 × n



### Variant 4: Surrounding Junctions Lagged



Plain Dataset + lagged values for all 3 metrics of `m` adjacent junctions (spatially defined)

**Total columns**: 30 + 3 × n × m

Example: if n = 5 and m = 3 → 30 + 45 = 75



### Variant 5: Full Lagged Dataset



For each of the 10 junctions, include current + n lagged values for all 3 metrics

**Total columns**: (n + 1) × 3 × 10

Example: if n = 5 → 6 × 3 × 10 = 180



---



## Example of Lag Feature Generation



Assume we are lagging only FP_D_Count with n = 3.



**Original data:**



| Time | FP_D_Count |

| ---- | ------------ |

| t=0  | 100          |

| t=1  | 120          |

| t=2  | 115          |

| t=3  | 130          |

| t=4  | 125          |



**After adding lag features:**



| Time | FP_D_Count (t) | t-1 | t-2 | t-3 |

| ---- | ---------------- | --- | --- | --- |

| t=3  | 130              | 115 | 120 | 100 |

| t=4  | 125              | 130 | 115 | 120 |



The first n rows (t=0 to t=2) are excluded as they don't have full lag context.



---



## Modeling Notes

* Lagging should be done after downsampling

* Input features use only information available up to and including time `t` (no future leakage)

* Target prediction is FP_D_Count at time `t`

* Data must be split temporally, not randomly, for train/val/test

* For deep models (RNN, LSTM, GRU, Transformer), inputs should be shaped as:

&nbsp; [samples, sequence_length = n + 1, features_per_step]



---



## Feature Column Summary (for n = 5, m = 3)



| Variant               | Formula          | Total Columns |

| --------------------- | ---------------- | ------------- |

| Plain                 | 10 × 3           | 30            |

| Target Lagged         | 30 + 5           | 35            |

| Target Metrics Lagged | 30 + 3 × 5       | 45            |

| Surrounding Lagged    | 30 + 3 × 5 × 3   | 75            |

| Full Lagged           | (5 + 1) × 3 × 10 | 180           |



