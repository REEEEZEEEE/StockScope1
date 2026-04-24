from flask import Flask, request, jsonify, send_from_directory
from flask_admin import Admin
from flask_cors import CORS
from datetime import datetime
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


app = Flask(__name__, static_folder="build", static_url_path="/")
CORS(app)  # Optional but helpful during dev

# --- Your API Endpoint Example ---
@app.route("/api/info/<ticker>")
def get_info(ticker):
    return jsonify({"ticker": ticker, "message": "Backend Connected ✅"})

# --- Serve React frontend ---
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# For React Router Support:
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")

def calculate_metrics(ticker):
    data = yf.download(ticker, period="1y")
    stock=yf.download(ticker, period="5y",interval="1mo").dropna()
    market = yf.download("^GSPC", period="1y")['Close']
    if data.empty or stock.empty:
        raise ValueError("No data found for ticker")

    data["Returns"] = data["Close"].pct_change()
    mean_return = float((data["Close"].iloc[-1] - data["Close"].iloc[0])/data["Close"].iloc[0])
    volatility = float(data["Returns"].std() * np.sqrt(252))
    sharpe_ratio = float(mean_return / volatility) if volatility != 0 else 0.0
    current_price = float(data["Close"].iloc[-1])
    stock_returns = data['Close'].pct_change().dropna()
    market_returns = market.pct_change().dropna()
    betadata = pd.concat([stock_returns, market_returns], axis=1)
    betadata.columns = ['stock', 'market']
    covariance = betadata.cov().iloc[0,1]
    variance = betadata['market'].var()

    beta = covariance / variance
    beta=round(beta, 3)

    rolling_max = data['Close'].cummax()

    drawdown = (data['Close'] / rolling_max) - 1

    rolling_max1 = stock['Close'].cummax()

    drawdown1 = (stock['Close'] / rolling_max1) - 1

    max_drawdown1 = drawdown1.values.min()  # most negative value
    max_drawdown1=round(max_drawdown1 * 100, 2)

    max_drawdown = drawdown.values.min()  # most negative value
    max_drawdown=round(max_drawdown * 100, 2)  # return percent
    
    dates=[]
    dates=stock.reset_index()
    dates=dates['Date'].dt.strftime("%m %b %Y").tolist()
    prices=[]
    prices=stock['Close'].values.round(2).tolist()
    finalprices=[]
    for item in prices:
        finalprices.extend(item)


    ml = yf.download(ticker, period="10y").dropna()

    # Use closing prices
    prices = ml["Close"].values

    # X = time (days), y = price
    X = np.arange(len(prices)).reshape(-1, 1)
    y = prices

    model = LinearRegression()
    model.fit(X, y)

    # Predict future days
    last_day = len(prices)

    pred_1y = model.predict([[last_day + 252]])[0]   # 252 trading days
    pred_5y = model.predict([[last_day + 252*5]])[0]
    pred_10y = model.predict([[last_day + 252*10]])[0]

    current_price1 = prices[-1]
    


    mlp = yf.download(ticker, period="10y").dropna()

    prices2 = mlp["Close"].values
    dates2 = mlp.index

    # Train model
    X = np.arange(len(prices2)).reshape(-1, 1)
    y = prices2

    model = LinearRegression()
    model.fit(X, y)

    # Generate future timeline (10 years monthly)
    months = 120  # 10 years * 12 months
    last_index = len(prices2)

    future_indices = np.array([
        last_index + i * 21 for i in range(months)
    ]).reshape(-1, 1)  # ~21 trading days per month

    prediction7 = model.predict(future_indices)
    finalpredictions=[]
    for item in prediction7:
        finalpredictions.extend(item)
    # Generate future dates (monthly)
    last_date = dates2[-1]
    future_dates = pd.date_range(start=last_date, periods=months+1, freq='M')[1:]


        


    metrics = {
        "ticker": ticker.upper(),
        "current_price": round(current_price, 2),
        "annual_return": round(mean_return * 100, 2),
        "volatility": round(volatility * 100, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "dates": dates,
        "prices": finalprices,
        "beta": beta,
        "max_drawdown": max_drawdown,
        "max_drawdown1": max_drawdown1,
        "current": float(current_price1),
        "pred_1y": float(pred_1y),
        "pred_5y": float(pred_5y),
        "pred_10y": float(pred_10y),
        "future_dates": future_dates.strftime("%Y-%m-%d").tolist(),
        "future_prices": finalpredictions
    }
    return metrics

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        ticker = data.get("ticker", "").strip().upper()
        if not ticker:
            return jsonify({"success": False, "error": "Ticker is required"})
        
        metrics = calculate_metrics(ticker)
        return jsonify({"success": True, "metrics": metrics})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
