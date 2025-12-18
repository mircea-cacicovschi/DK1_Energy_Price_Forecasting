# DK1 Energy Price Forecasting

This repository contains all code used in my Master's Thesis:
"Comparative Evaluation of Machine Learning and Deep Learning Models for Day-Ahead Electricity Price Forecasting in the DK1 Market."

The project builds a complete forecasting framework that evaluates many model families. It includes traditional machine learning models, deep learning architectures, and baseline models. All models are trained and evaluated using expanding window cross validation to simulate real world forecasting.

---

## Project Overview

The goal of the thesis is to predict day-ahead electricity prices for the Danish DK1 market. The project compares a wide range of model classes to identify which methods provide robust performance under realistic forecasting conditions.

Machine Learning Models:
- Lasso Regression  
- Ridge Regression  
- Elastic Net  
- Random Forest  
- Gradient Boosting  
- Bagging Regressor  
- Support Vector Regression  
- k-Nearest Neighbors  
- Multivariate Adaptive Regression Splines (MARS)

Deep Learning Models:
- Feedforward Neural Network (FNN)  
- Long Short-Term Memory (LSTM)  
- Gated Recurrent Unit (GRU)  
- Convolutional Neural Network (CNN)  
- Temporal Convolutional Network (TCN)

Baseline Model:
- Seasonal Naive (weekly seasonality with 365 days of initial data)

---

## Data Description

The project uses daily DK1 electricity price data combined with 14-day weather forecasts from 45 Danish meteorological stations. Key variables include:

- Temperature  
- Wind speed  
- Humidity  
- Cloud cover  
- Radiation  
- Precipitation  

Engineered features include lag structures, rolling averages, weather forecast transformations, and calendar effects.

Raw datasets are **not included** in the repository. Users must generate the data using the provided scripts.

---

## Data Access and Generation

All generated datasets are saved directly in the same folder as the scripts.  
There is no separate data directory.

Other scripts expect to load files using simple filenames (for example: `"example.csv"`) without any folder path.

To generate the required datasets, run the following scripts from inside the repository folder:

python energy_data_API.py  
python DMI_temp.py  
python DMI_wind.py  
python DMI_hum.py  
python DMI_cloud.py  
python DMI_precip.py  
python DMI_rad.py  

Make sure you are in the repository folder when running these scripts so that all output files are saved correctly.

---

## Cross Validation Strategy

All models use expanding window cross validation (rolling origin evaluation). This approach simulates real world forecasting by gradually expanding the training window while keeping evaluation periods fixed.

Key details:
- Forecast horizon: 14 days  
- Multiple rolling origins  
- Metrics used: MAE, RMSE, MAPE  
- Final pseudo test: 1 to 14 August 2025  

This strategy provides a realistic estimate of model performance and prevents data leakage.

---

## Repository Structure

The repository uses a flat layout. All scripts, data generation tools, model training code, notebooks, and output files are stored in the same directory.

DK1_Energy_Price_Forecasting/  
  energy_data_API.py              (Downloads DK1 electricity price data via ENTSO-E API)  
  merged_data.py                  (Merges price data with weather forecasts into a unified dataset)  
  DMI_temp.py                     (Downloads and processes historical temperature data)  
  DMI_wind.py                     (Downloads and processes historical wind speed data)  
  DMI_hum.py                      (Downloads and processes historical humidity data)  
  DMI_cloud.py                    (Downloads and processes historical cloud cover data)  
  DMI_precip.py                   (Downloads and processes historical precipitation data)  
  DMI_rad.py                      (Downloads and processes historical radiation data)  
  forecasted_variables.py         (Downloads and aggregates weather forecasts across all 45 DK1 stations)  
  test_energy_prices_aug2025.py   (Pseudo-test evaluation script for 1 to 14 August 2025)  
  one_station.py                  (Processes and visualizes data for a single weather station)  
  regions_DK.py                   (Defines regions and station groupings used in data aggregation)  
  testing.py                      (General testing and debugging utilities)  
  thesis work v3.qmd              (Quarto document containing model training and analysis)  
  test set.qmd                    (Quarto file for test set documentation and evaluation)  
  thesis plots etc.R              (R script for generating plots used in the thesis)  
  Deep Learning Models.ipynb      (Training notebook for FNN, LSTM, GRU, CNN, and TCN models)  
  Pseudo-test set DL.ipynb        (Evaluation notebook for deep learning models on the pseudo-test period)  
  requirements.txt                (Python dependencies)  
  requirements_r.txt              (R dependencies)  
  .gitignore                      (Ignored files and generated outputs)  
  README.md                       (This file)  
  (generated CSV files)           (Created automatically when running data scripts)

No subfolders are required. All scripts operate on files stored in the same directory.

---

## Notebooks

Two Google Colab notebooks are included in the repository.

**Deep Learning Models.ipynb**  
This notebook contains the training workflow for multiple deep learning models, including Feedforward Neural Networks, LSTM, GRU, CNN, and TCN. It includes model setup, training loops, hyperparameters, and validation results.

**Pseudo-test set DL.ipynb**  
This notebook evaluates the best performing deep learning models on the pseudo-test period from 1 to 14 August 2025. It reconstructs forecasts, applies inverse scaling, and calculates MAE, RMSE, and MAPE.

> Both notebooks are committed **without cell outputs** for readability.  
> All results reported in the README were generated using this code.

---

## Environment Setup

This project uses both Python and R.

### Python
Install required Python packages:

pip install -r requirements.txt  

### R
Install required R packages:

install.packages(readLines("requirements_r.txt"))

Alternatively, if using renv:

install.packages("renv")  
renv::restore()

---

## API Keys and Environment Variables

Some data collection scripts require external API keys. For security reasons, API keys are **not stored in this repository**.

Required environment variables:
- DMI_API_KEY     (used by DMI weather data scripts)
- ENTSOE_API_KEY  (used by ENTSO-E electricity price scripts)

Set these variables before running any data collection scripts.

---

## How to Run the Code

1. Clone the repository:

git clone https://github.com/mircea-cacicovschi/DK1_Energy_Price_Forecasting.git  
cd DK1_Energy_Price_Forecasting  

2. Install Python dependencies:

pip install -r requirements.txt  

3. (Optional) Install R dependencies if running R scripts or Quarto files.

4. Set required environment variables (API keys).

5. Generate datasets by running the data scripts.

6. Run preprocessing:

python merged_data.py  

7. Train machine learning or deep learning models using the available Python scripts, R scripts, or notebooks.

---

## Results Summary

Model | MAE | RMSE | Notes  
------|------|--------|--------  
Seasonal Naive | 25.08 | 30.99 | Baseline  
Lasso | 13.58 | 17.05 | Linear model, moderate performance  
**Ridge** | **8.16** | **9.95** | **Best overall performance across all models**  
Elastic Net | 13.58 | 17.02 | Similar to Lasso  
Bagging | 14.45 | 18.09 | Ensemble method  
Random Forest | 14.28 | 17.84 | Strong ML model, stable  
Gradient Boosting | 13.64 | 16.89 | Stable and accurate  
XGBoost | 13.78 | 17.33 | Boosting method  
SVR | 12.87 | 16.19 | Strong nonlinear performance  
KNN Regression | 23.69 | 28.65 | Poor performance on this dataset  
MARS | 14.50 | 17.93 | Flexible spline model  
Feedforward NN | 26.68 | 32.24 | Underperforms, likely due to limited data  
LSTM | 31.57 | 38.52 | Initial deep learning baseline  
GRU | 30.37 | 37.27 | Similar to LSTM  
CNN | 32.50 | 39.86 | Not suitable for this task  
TCN | 29.01 | 36.26 | Best deep learning model, still below ML models  

**Ridge Regression clearly outperformed all other models, achieving an MAE of 8.16 and RMSE of 9.95, while every deep learning architecture underperformed by a wide margin on the DK1 day-ahead forecasting task.**
