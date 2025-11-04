import React, { useState, useEffect } from 'react'
import axios from 'axios'

const TradingChart = () => {
  const [marketData, setMarketData] = useState([])
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const API_BASE = 'http://localhost:5000/api'

  useEffect(() => {
    loadMarketData()
  }, [selectedSymbol])

  const loadMarketData = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await axios.get(`${API_BASE}/market/data?symbol=${selectedSymbol}`)
      if (response.data.status === 'success') {
        setMarketData(response.data.data)
      } else {
        setError('No market data available')
      }
    } catch (err) {
      setError('Error loading market data: ' + err.message)
      console.error('Error loading market data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSymbolChange = (event) => {
    setSelectedSymbol(event.target.value)
  }

  if (loading) {
    return (
      <div className="card">
        <h2>Market Charts</h2>
        <div className="loading">Loading market data for {selectedSymbol}...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <h2>Market Charts</h2>
        <div className="error">{error}</div>
        <button className="btn" onClick={loadMarketData} style={{ marginTop: '10px', background: '#2196f3' }}>
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h2>Market Data - {selectedSymbol}</h2>
        <select 
          value={selectedSymbol} 
          onChange={handleSymbolChange}
          style={{ 
            padding: '8px', 
            background: '#252547', 
            color: 'white', 
            border: '1px solid #333', 
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          <option value="AAPL">Apple (AAPL)</option>
          <option value="MSFT">Microsoft (MSFT)</option>
          <option value="GOOGL">Google (GOOGL)</option>
          <option value="TSLA">Tesla (TSLA)</option>
        </select>
      </div>
      
      {marketData.length > 0 ? (
        <>
          {/* Price History Table */}
          <div style={{ background: '#252547', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
            <h3 style={{ color: '#00d4ff', marginBottom: '15px', textAlign: 'center' }}>Price History</h3>
            {marketData.map((day, index) => {
              const isPositive = day.change >= 0
              
              return (
                <div 
                  key={index}
                  style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    padding: '10px 0', 
                    borderBottom: index < marketData.length - 1 ? '1px solid #333' : 'none',
                    alignItems: 'center',
                    background: index % 2 === 0 ? 'rgba(255,255,255,0.05)' : 'transparent',
                    borderRadius: '4px',
                    margin: '2px 0'
                  }}
                >
                  <div style={{ flex: 1, color: '#ccc', fontWeight: 'bold' }}>{day.date}</div>
                  <div style={{ flex: 1, textAlign: 'center', fontWeight: 'bold', color: '#00d4ff' }}>
                    ${day.close}
                  </div>
                  <div 
                    style={{ 
                      flex: 1, 
                      textAlign: 'right',
                      color: isPositive ? '#00c853' : '#ff4444',
                      fontWeight: 'bold',
                      fontSize: '1.1em'
                    }}
                  >
                    {isPositive ? '📈' : '📉'} {isPositive ? '+' : ''}{day.change}%
                  </div>
                </div>
              )
            })}
          </div>

          {/* Summary Statistics */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginBottom: '20px' }}>
            <div className="metric">
              <div className="metric-value">${marketData[marketData.length - 1]?.close}</div>
              <div className="metric-label">Current Price</div>
            </div>
            <div className="metric">
              <div className="metric-value">${marketData[0]?.close}</div>
              <div className="metric-label">Start Price</div>
            </div>
            <div className="metric">
              <div className={`metric-value ${
                marketData[marketData.length - 1]?.close >= marketData[0]?.close ? 'positive' : 'negative'
              }`}>
                {((marketData[marketData.length - 1]?.close - marketData[0]?.close) / marketData[0]?.close * 100).toFixed(2)}%
              </div>
              <div className="metric-label">Total Change</div>
            </div>
          </div>

          {/* Volume Information */}
          <div style={{ background: '#252547', padding: '15px', borderRadius: '8px' }}>
            <h3 style={{ color: '#00d4ff', marginBottom: '15px', textAlign: 'center' }}>Volume Information</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div className="metric">
                <div className="metric-value">
                  {(marketData.reduce((sum, day) => sum + day.volume, 0) / 1000000).toFixed(1)}M
                </div>
                <div className="metric-label">Total Volume</div>
              </div>
              <div className="metric">
                <div className="metric-value">
                  {(marketData.reduce((sum, day) => sum + day.volume, 0) / marketData.length / 1000000).toFixed(1)}M
                </div>
                <div className="metric-label">Avg Daily Volume</div>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="loading">No market data available for {selectedSymbol}</div>
      )}
    </div>
  )
}

export default TradingChart