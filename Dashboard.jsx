import React, { useState, useEffect } from 'react'
import axios from 'axios'

const Dashboard = () => {
  const [metrics, setMetrics] = useState({})
  const [recentTrades, setRecentTrades] = useState([])
  const [debugInfo, setDebugInfo] = useState('')
  const [loading, setLoading] = useState(true)

  const API_BASE = 'http://localhost:5000/api'

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const [portfolioRes, tradesRes] = await Promise.all([
        axios.get(`${API_BASE}/portfolio`),
        axios.get(`${API_BASE}/trades`)
      ])

      if (portfolioRes.data.status === 'success') {
        setMetrics(portfolioRes.data.portfolio)
      }

      if (tradesRes.data.status === 'success') {
        setRecentTrades(tradesRes.data.trades.slice(-5))
      }
      setDebugInfo('✅ Data loaded successfully')
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setDebugInfo('❌ Error connecting to API: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const testConnection = async () => {
    try {
      const response = await axios.get(`${API_BASE}/health`)
      setDebugInfo(`✅ API Health: ${response.data.status} - ${new Date().toLocaleTimeString()}`)
    } catch (error) {
      setDebugInfo('❌ API Connection Failed: ' + error.message)
    }
  }

  if (loading) {
    return (
      <div className="card">
        <h2>Dashboard</h2>
        <div className="loading">Loading dashboard data...</div>
      </div>
    )
  }

  return (
    <div>
      <div className="card">
        <h2>🔧 Debug Information</h2>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
          <button className="btn" onClick={testConnection} style={{ background: '#ff9800' }}>
            Test Connection
          </button>
          <button className="btn" onClick={fetchDashboardData} style={{ background: '#2196f3' }}>
            Refresh Data
          </button>
        </div>
        {debugInfo && (
          <div className="debug">
            {debugInfo}
          </div>
        )}
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h2>📊 Portfolio Overview</h2>
          {metrics.total_value ? (
            <div className="metrics">
              <div className="metric">
                <div className="metric-value">${metrics.total_value?.toLocaleString()}</div>
                <div className="metric-label">Total Value</div>
              </div>
              <div className="metric">
                <div className="metric-value">${metrics.cash_balance?.toLocaleString()}</div>
                <div className="metric-label">Cash Balance</div>
              </div>
              <div className="metric">
                <div className={`metric-value ${metrics.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                  {metrics.total_pnl >= 0 ? '+' : ''}${metrics.total_pnl?.toLocaleString()}
                </div>
                <div className="metric-label">Total P&L</div>
              </div>
              <div className="metric">
                <div className={`metric-value ${metrics.total_pnl_pct >= 0 ? 'positive' : 'negative'}`}>
                  {metrics.total_pnl_pct >= 0 ? '+' : ''}{metrics.total_pnl_pct?.toFixed(2)}%
                </div>
                <div className="metric-label">Return %</div>
              </div>
            </div>
          ) : (
            <div className="loading">No portfolio data available</div>
          )}
        </div>

        <div className="card">
          <h2>📈 Recent Trades</h2>
          {recentTrades.length > 0 ? (
            <table className="table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Action</th>
                  <th>Qty</th>
                  <th>Price</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {recentTrades.map((trade) => (
                  <tr key={trade.id}>
                    <td>{trade.symbol}</td>
                    <td className={trade.action.toLowerCase()}>{trade.action}</td>
                    <td>{trade.quantity}</td>
                    <td>${trade.price}</td>
                    <td>{new Date(trade.timestamp).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="loading">No recent trades</div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard