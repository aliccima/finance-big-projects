# Finance Package

## Overview

The `FinanceModels` package provides a set of financial models and operations, interfacing with an external API for data. It includes methods to calculate the Capital Asset Pricing Model (CAPM), Black-Scholes option pricing model and Historical Simulation model.

## Features

* CAPM Calculation: Compute the alpha value of a given stock using the Capital Asset Pricing Model.
* Black-Scholes Model: Calculate the theoretical price of call and put options.
* Historical Simulation model: Compute the Value at Risk using the historical simulation method.
* API Integration: Fetch financial data such as stock prices, beta values, risk-free rate, and market returns from an external API.

## Installation

To install the `FinanceModels` package, use the following command:
```sh
pip install git+https://github.com/aliccima/finance_package.git
```

## Usage

### Initialization

Initialize the `FinanceModels` class with the API URI:
```py
from finance_package import FinanceModels

api_uri = "https://api.example.com"
finance_model = FinanceModels(api_uri=api_uri)
```

### CAPM Calculation

Calculate the CAPM alpha value for a given stock:
```python
ticker = 'AAPL'
alpha = finance_model.CAPM(ticker)
print(f"CAPM Alpha for {ticker}: {alpha}")
```

### Black-Scholes Option Pricing

Calculate the Black-Scholes price for a call or put option:
```python
ticker = 'AAPL'
option_type = 'call'
strike_price = 150
time_to_maturity = 0.5  # in years

option_price = finance_model.Black_Scholes(ticker, option_type, strike_price, time_to_maturity)
print(f"Black-Scholes {option_type} option price for {ticker}: {option_price}")
```

### Historical Simulation

Calculate the Value at Risk for a given stock using the historical simulation method:
```python
ticker = 'AAPL'
confidence_level = 0.95

VaR = finance_model.historical_simulation(ticker, confidence_level)
print(f"Historical Simulation VaR for AAPL at 95% confidence level: {VaR}")
```

## License

This project is licensed under the MIT License.
