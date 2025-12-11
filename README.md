# DK1 Energy Price Forecasting

This repository contains all code used in my Master's Thesis:  
"Comparative Evaluation of Machine Learning and Deep Learning Models for Day-Ahead Electricity Price Forecasting in the DK1 Market."

The project builds a complete forecasting framework that evaluates many model families. It includes traditional machine learning, deep learning architectures, and baseline models. All models are trained and evaluated using expanding window cross validation to simulate real world forecasting.

---

## Project Overview

The goal of the thesis is to predict day-ahead electricity prices for the Danish DK1 market. The project compares many model classes to identify which methods provide robust performance under realistic forecasting conditions.

### Machine Learning Models
- Lasso Regression  
- Ridge Regression  
- Elastic Net  
- Random Forest  
- Gradient Boosting  
- Bagging Regressor  
- Support Vector Regression  
- k-Nearest Neighbors  
- Multivariate Adaptive Regression Splines (MARS)

### Deep Learning Models
- Feedforward Neural Network (FNN) 
- Long Short-Term Memory (LSTM)
- Gated Recurrent Unit (GRU)
- Convolutional Neural Network (CNN)
- Temporal Convolutional Network (TCN)

### Baseline Model
- Seasonal Naive (weekly seasonality with 365 days of initial data)  

---

## Data Description

The project uses daily DK1 electricity price data combined with 14 day weather forecasts from 45 Danish meteorological stations. Key weather variables include:

- Temperature  
- Wind speed  
- Humidity  
- Cloud cover  
- Radiation  
- Precipitation  

Additional engineered features include:

- Lag features  
- Rolling averages  
- Weather forecast transformations  
- Calendar features  

Raw datasets are not included in the repository. Users must generate the data using the provided scripts.





