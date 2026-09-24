# Machine Learning Delay Prediction Pipeline

## 1. Problem Definition & Target
* **Target Variable:** `taxi_delay_minutes` (Continuous non-negative float representing runway queue and taxi-in delay).
* **Derivation:** Measures duration from touchdown to gate arrival minus nominal unimpeded taxi duration.

## 2. Feature Engineering & Strict Leakage Prevention
To prevent lookahead data leakage, features only include information accessible prior to flight arrival:
1. **Temporal Features:**
   * `hour`, `day_of_week`, `month`, `is_weekend`, `is_peak_hour`
2. **Flight Dynamics:**
   * `airline`, `aircraft_type`, `origin`, `destination`, `terminal`, `runway`, `scheduled_duration_minutes`, `turnaround_minutes`
3. **Airport Congestion:**
   * `active_flights`, `flights_per_hour`, `arrivals_per_hour`, `departures_per_hour`
4. **Meteorological Indicators:**
   * `temperature` (°C), `wind_speed` (knots), `visibility` (km), `precipitation` (mm), `weather_condition`

## 3. Evaluation Metrics Explained

### Mean Absolute Error (MAE)
$$\text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|$$
Measures the average magnitude of delay errors in physical minutes.

### Root Mean Squared Error (RMSE)
$$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2}$$
Heavily penalizes extreme operational delay prediction errors.

### Coefficient of Determination ($R^2$)
$$R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$
Quantifies the proportion of delay variance explained by operational and meteorological covariates.

## 4. Chronological Validation Split
Flight delays are time-correlated. A chronological split (70% Train, 15% Validation, 15% Test) is strictly enforced to simulate real production forecasting without future information leaking into the training set.

## 5. Model Tournament Results
| Model Candidate | Validation MAE | Validation RMSE | Validation $R^2$ | Test MAE | Test $R^2$ | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Linear Regression** | 3.54 min | 4.45 min | 0.8012 | 3.48 min | 0.8023 | Baseline |
| **Random Forest Regressor** | 3.53 min | 4.46 min | 0.7999 | 3.53 min | 0.7974 | Evaluated |
| **Gradient Boosting Regressor** | **3.51 min** | **4.40 min** | **0.8057** | **3.51 min** | **0.7985** | **Champion** |
