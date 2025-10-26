import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";
import axios from "axios";
import "./App.css";

function App() {
  const [ticker, setTicker] = useState("");
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMetrics(null);
    try {
      const response = await axios.post("http://127.0.0.1:5000/analyze", { ticker });
      if (response.data.success) {
        setMetrics(response.data.metrics);
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError("Failed to fetch data. Make sure Flask is running.");
    }
  };

  return (
    <div className="App">
      <div class ="top-title">
      <h1>Stock Analyzer</h1>
      </div>
      <div class="search">
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Enter Stock Ticker"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
          />
          <button type="submit">Analyze</button>
        </form>
      </div>

      {error && <p className="error">{error}</p>}

      {metrics && (
        <div className="card">
          <div class="title">
          <h2>{metrics.ticker}</h2>
          </div>
          <div class="centered">
            <div class="item">
              <p><strong>Current Price:</strong></p>
              <div class="price-current">
              <p class="text"> ${metrics.current_price}</p> 
              </div>
            </div>
            <div class="item">
              <p><strong>Annual Return:</strong></p>
              <p class="text"> 
                <span style={{  
                  color:
                    metrics.annual_return > 15
                      ? "green"
                      : metrics.annual_return < 7
                      ? "red"
                      : "orange",
                  fontWeight: "bold",
                }}>
                {metrics.annual_return}%
                </span>
              </p>
            </div>
            <div class="item">
              <p><strong>Volatility:</strong></p>
              <p class="text">
              <span style={{  
                  color:
                    metrics.volatility > 20
                      ? "green"
                      : metrics.volatility < 10
                      ? "red"
                      : "orange",
                  fontWeight: "bold",
                }}>
                {metrics.volatility}%
                </span>
              </p>
            </div>
            <div class="item">
              <p>
                <strong>Sharpe Ratio:</strong> 
              </p>
              <p class="text">
                <span style={{  
                  color:
                    metrics.sharpe_ratio > 1
                      ? "green"
                      : metrics.sharpe_ratio < 0.5
                      ? "red"
                      : "orange",
                  fontWeight: "bold",
                }}>
                {metrics.sharpe_ratio}
                </span>
                  
              </p>
            </div>
            </div>
            <div class="graph">
                <Plot 
                data={[
                  {
                    x: metrics.dates,
                    y: metrics.prices,
                    type: "scatter",
                    mode: "lines",
                    marker: { color: "blue" },
                  },
                ]}
                layout={{
                  title: "Stock Price Over Time",
                  xaxis: { title: "Date",
                          tickmode: "auto",
                          nticks: 10,
                           gridcolor: "#333"
                          
                   },
                  yaxis: { title: "Price (USD)",
                     gridcolor: "#333"
                   },
                  paper_bgcolor: "#151515",
                  plot_bgcolor: "#151515",
                  font: { color: "#ffffff" },
                  responsive: true,
                }}
                style={{ width: "100%"}}
              />
            </div>
              <div class="second-row">
              <div class="item">
                <p><strong>Beta:</strong></p>
                <p class="text">
                <span style={{  
                    color:
                      metrics.beta > 1
                        ? "green"
                        : metrics.beta < 1
                        ? "red"
                        : "orange",
                    fontWeight: "bold",
                  }}>
                  {metrics.beta}
                  </span>
                </p>
              </div>
              <div class="item">
                <p>
                  <strong>5 Year Max Drawdown:</strong> 
                </p>
                <p class="text">
                  <span style={{  
                    color:
                      metrics.max_drawdown > 25
                        ? "green"
                        : metrics.max_drawdown < 15
                        ? "red"
                        : "orange",
                    fontWeight: "bold",
                  }}>
                  {metrics.max_drawdown}%
                  </span>
                    
                </p>
              </div>
              </div>
        </div>
      )}
      <div class="disclaimer">
        <p>This is not finnancial advice</p>
      </div>
    </div>
  );
}

export default App;
