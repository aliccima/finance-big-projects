import numpy as np
import requests
from scipy.stats import norm


class FinanceModels:
    """
    A class to encapsulate various financial models and operations, interfacing with an external API for data.

    This class provides methods to calculate financial metrics such as the Capital Asset Pricing Model (CAPM),
    Black-Scholes option pricing model and historical simulation to calculate Value at Risk. It initializes with an API
    URI and retrieves essential financial data such as the risk-free rate and market return.
    """

    def __init__(self, api_uri: str) -> None:
        """
        Initialize the FinanceModels class with the given API URI.

        This constructor sets the base URI for the API and retrieves the initial values for the risk-free rate and
        market return by making API requests.

        Parameters:
        ----------
        api_uri : str
            The base URI of the API used for data requests.

        Example:
        -------
        >>> finance_model = FinanceModels(api_uri="https://api.example.com")
        """
        self.api_uri = api_uri

        self.risk_free = self._request("/prices", ticker="^IRX")["prices"][0]
        self.market_return = self._request("/prices", ticker="NQ=F")["prices"][0]

    def _request(self, endpoint: str, **body):
        """
        Send a POST request to the specified API endpoint with a JSON body.

        This method constructs and sends a POST request to the given API endpoint using the base URI that was given as
        `api_uri`. It includes a JSON body composed of keyword arguments passed to the method. The response is expected
        to be in JSON format.

        Parameters:
        ----------
        endpoint : str
            The API endpoint to which the request will be sent.
        **body : dict
            Arbitrary keyword arguments that form the JSON body of the POST request.

        Returns:
        -------
        dict
            The JSON response from the API, parsed into a dictionary if the request is successful (status code 200).
            Returns None if the request fails.

        Example:
        -------
        >>> finance_model._request('/beta', ticker='AAPL')
        {'beta': 1.2}  # Example output representing the beta value for the given ticker
        """

        headers = {
            "Content-Type": "application/json",
        }

        resp = requests.post(self.api_uri + endpoint, json=body, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            print("Failed to request data from API")
            print(resp.text)

    def CAPM(self, ticker: str) -> float:
        """
        Calculate the alpha value of a given stock using the Capital Asset Pricing Model (CAPM).

        The CAPM formula is used to determine the expected return of an asset based on its beta and the expected market
        return. The alpha is the difference between the real return and the theoretical return predicted by CAPM.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the stock for which to calculate the CAPM alpha value.

        Returns:
        -------
        float
            The alpha value, which is the difference between the real return and the theoretical return of the stock. A
            positive alpha indicates that the stock has performed better than predicted by CAPM, while a negative alpha
            indicates underperformance.

        Example:
        -------
        >>> finance_model.CAPM('AAPL')
        0.023  # Example output indicating the stock's performance relative to CAPM expectations
        """

        beta = self._request("/beta", ticker=ticker)["beta"]
        R_real = self._request("/prices", ticker=ticker)["prices"][0]

        R_theoretical = beta * (self.market_return - self.risk_free)
        alpha = R_real - R_theoretical
        return alpha

    def Black_Scholes(
        self,
        ticker: str,
        option_type: str,
        strike_price: float,
        time_to_maturity: float,
    ) -> float:
        """
        Calculate the Black-Scholes price for a call or put option.

        The Black-Scholes model is used to determine the theoretical price of call and put options based on various
        parameters, including the underlying asset price, strike price, time to maturity, risk-free rate, and
        volatility.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the stock for which to calculate the option price.
        option_type : str
            The type of the option, either "call" for a call option or "put" for a put option.
        strike_price : float
            The strike price of the option.
        time_to_maturity : float
            The time to maturity of the option, expressed in years.

        Returns:
        -------
        float
            The theoretical price of the option calculated using the Black-Scholes model.

        Example:
        -------
        >>> finance_model.Black_Scholes('AAPL', 'call', 150, 0.5)
        10.57  # Example output representing the call option price
        """
        # calculate volatility
        prices_yr = self._request("/prices", ticker=ticker, limit=252)["prices"]
        prices_yr = np.array(prices_yr)

        log_returns = np.log(prices_yr[:-1] / prices_yr[1:])
        sigma = np.std(log_returns) * np.sqrt(252)  # annualize the volatility

        # calculate variables for the model
        S = self._request("/prices", ticker=ticker)["prices"][0]
        K = strike_price
        T = time_to_maturity
        d1 = (np.log(S / K) + (self.risk_free + 0.5 * sigma**2) * T) / (
            sigma * np.sqrt(T)
        )
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == "call":
            price = S * norm.cdf(d1) - K * np.exp(-self.risk_free * T) * norm.cdf(d2)
        else:
            price = K * np.exp(-self.risk_free * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

        return price

    def historical_simulation(
        self, ticker: str, confidence_level: float = 0.95
    ) -> float:
        """
        Calculate the Value at Risk (VaR) for a given stock using the historical simulation method.

        The historical simulation method estimates VaR based on historical price movements of the stock. It assumes that
        historical returns are representative of future returns and uses these to simulate potential future losses.

        Parameters:
        ----------
        ticker : str
            The ticker symbol of the stock for which to calculate the VaR.
        confidence_level : float, optional
            The confidence level for the VaR calculation, by default 0.95 (95%).

        Returns:
        -------
        float
            The estimated Value at Risk (VaR) at the specified confidence level.

        Example:
        -------
        >>> VaR = finance_model.historical_simulation('AAPL', 0.95)
        >>> print(f"Historical Simulation VaR for AAPL at 95% confidence level: {VaR}")
        Historical Simulation VaR for AAPL at 95% confidence level: 0.045  # Example output
        """
        prices_yr = self._request("/prices", ticker=ticker, limit=252)["prices"]
        prices_yr = np.array(prices_yr)

        # calculate log returns
        log_returns = np.log(prices_yr[:-1] / prices_yr[1:])
        sorted_log_returns = np.sort(log_returns)

        # Calculate the VaR
        index = int((1 - confidence_level) * len(sorted_log_returns))
        VaR = sorted_log_returns[index]
        return np.abs(VaR)
