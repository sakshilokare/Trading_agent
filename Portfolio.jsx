import React, { useState, useEffect } from 'react'
import axios from 'axios'

const Portfolio = () => {
  const [portfolio, setPortfolio] = useState({})
  const [tradeHistory, setTradeHistory] = useState([])
  const [loading, setLoading] = useState(true)

  const API_BASE = 'http://localhost:5000/api'

  useEffect(() => {
    fetchPortfolioData()
    const interval = setInterval(fetchPortfolioData, 15000)
    return () => clearInterval(interval)
  }, [])

  const fetchPortfolioData = async () => {
    try {
      setLoading(true)
      const [portfolioRes, tradesRes] = await Promise.all([
        axios.get(`${API_BASE}/portfolio`),
        axios.get(`${API_BASE}/trades`)
      ])

      if (portfolioRes.data.status === 'success') {
        setPortfolio(portfolioRes.data.portfolio)
      }

      if (tradesRes.data.status === 'success') {
        setTradeHistory(tradesRes.data.trades)
      }
    } catch (error) {
      console.error('Error fetching portfolio data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="card">
        <h2>Portfolio</h2>
        <div className="loading">Loading portfolio data...</div>
      </div>
    )
  }

  return (
    <div className="grid grid-2">
      <div className="card">
        <h2>Current Positions</h2>
        {portfolio.positions && Object.keys(portfolio.positions).length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Quantity</th>
                <th>Avg Price</th>
                <th>Current Price</th>
                <th>Value</th>
                <th>P&L</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(portfolio.positions).map(([symbol, position]) => (
                <tr key={symbol}>
                  <td style={{ fontWeight: 'bold' }}>{symbol}</td>
                  <td>{position.quantity}</td>
                  <td>${position.avg_price?.toFixed(2) || 'N/A'}</td>
                  <td>${position.current_price?.toFixed(2)}</td>
                  <td>${position.value?.toFixed(2)}</td>
                  <td className={position.pnl >= 0 ? 'positive' : 'negative'}>
                    ${position.pnl?.toFixed(2)} ({position.pnl_pct?.toFixed(2)}%)
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="loading">No active positions</div>
        )}

        {/* Portfolio Summary */}
        {portfolio.total_value && (
          <div style={{ marginTop: '20px', padding: '15px', background: '#252547', borderRadius: '8px' }}>
            <h3 style={{ color: '#00d4ff', marginBottom: '10px' }}>Portfolio Summary</h3>
            <div className="metrics">
              <div className="metric">
                <div className="metric-value">${portfolio.total_value?.toLocaleString()}</div>
                <div className="metric-label">Total Value</div>
              </div>
              <div className="metric">
                <div className="metric-value">${portfolio.cash_balance?.toLocaleString()}</div>
                <div className="metric-label">Cash</div>
              </div>
              <div className="metric">
                <div className={`metric-value ${portfolio.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                  {portfolio.total_pnl >= 0 ? '+' : ''}${portfolio.total_pnl?.toLocaleString()}
                </div>
                <div className="metric-label">Total P&L</div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h2>Trade History</h2>
        {tradeHistory.length > 0 ? (
          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Symbol</th>
                  <th>Action</th>
                  <th>Qty</th>
                  <th>Price</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {tradeHistory.map((trade) => (
                  <tr key={trade.id}>
                    <td style={{ fontSize: '0.9em' }}>{new Date(trade.timestamp).toLocaleString()}</td>
                    <td style={{ fontWeight: 'bold' }}>{trade.symbol}</td>
                    <td className={trade.action.toLowerCase()}>{trade.action}</td>
                    <td>{trade.quantity}</td>
                    <td>${trade.price}</td>
                    <td style={{ color: '#00c853' }}>{trade.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="loading">No trade history available</div>
        )}
      </div>
    </div>
  )
}

export default Portfolio