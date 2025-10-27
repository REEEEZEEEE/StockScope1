from flask import Flask, request, jsonify, send_from_directory
from flask_admin import Admin
from flask_cors import CORS
from datetime import datetime
import yfinance as yf
import numpy as np
import pandas as pd

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
        "max_drawdown1": max_drawdown1
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
