import React, { useState, useEffect } from 'react'
import axios from 'axios'

const Signals = () => {
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState('')

  const API_BASE = 'http://localhost:5000/api'

  useEffect(() => {
    fetchSignals()
    const interval = setInterval(fetchSignals, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchSignals = async () => {
    try {
      const response = await axios.get(`${API_BASE}/signals`)
      if (response.data.status === 'success') {
        setSignals(response.data.signals)
        setLastUpdated(new Date().toLocaleTimeString())
      }
    } catch (error) {
      console.error('Error fetching signals:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSignalColor = (action) => {
    switch (action) {
      case 'BUY': return 'positive'
      case 'SELL': return 'negative'
      case 'HOLD': return 'hold'
      default: return ''
    }
  }

  const getSignalIcon = (action) => {
    switch (action) {
      case 'BUY': return '🟢'
      case 'SELL': return '🔴'
      case 'HOLD': return '🟡'
      default: return '⚪'
    }
  }

  if (loading) {
    return (
      <div className="card">
        <h2>🎯 Trading Signals</h2>
        <div className="loading">Loading trading signals...</div>
      </div>
    )
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>🎯 Trading Signals</h2>
        {lastUpdated && (
          <div style={{ color: '#ccc', fontSize: '0.9em' }}>
            Last updated: {lastUpdated}
          </div>
        )}
      </div>
      
      {signals.length > 0 ? (
        <div className="grid grid-2">
          {signals.map((signal, index) => (
            <div 
              key={index} 
              className="card" 
              style={{ 
                border: `2px solid ${
                  signal.action === 'BUY' ? '#00c853' : 
                  signal.action === 'SELL' ? '#ff4444' : '#ffa726'
                }`,
                background: 'rgba(37, 37, 71, 0.8)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#00d4ff' }}>
                  {signal.symbol}
                </div>
                <div style={{ fontSize: '2rem' }}>
                  {getSignalIcon(signal.action)}
                </div>
              </div>
              
              <div 
                className={getSignalColor(signal.action)} 
                style={{ 
                  fontSize: '2rem', 
                  marginBottom: '15px',
                  textAlign: 'center',
                  fontWeight: 'bold',
                  textShadow: '0 0 10px rgba(0,0,0,0.5)'
                }}
              >
                {signal.action}
              </div>
              
              <div style={{ display: 'grid', gap: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#ccc' }}>Confidence:</span>
                  <span style={{ 
                    color: signal.confidence > 0.7 ? '#00c853' : signal.confidence > 0.5 ? '#ffa726' : '#ff4444',
                    fontWeight: 'bold'
                  }}>
                    {(signal.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#ccc' }}>Price:</span>
                  <span style={{ color: '#00d4ff', fontWeight: 'bold' }}>
                    ${signal.price?.toFixed(2)}
                  </span>
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#ccc' }}>Quantity:</span>
                  <span style={{ color: '#fff', fontWeight: 'bold' }}>
                    {signal.quantity} shares
                  </span>
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#ccc' }}>Signal Strength:</span>
                  <span style={{ color: '#fff', fontWeight: 'bold' }}>
                    {signal.confidence > 0.8 ? 'Strong' : signal.confidence > 0.6 ? 'Medium' : 'Weak'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="loading">No active trading signals available</div>
      )}
    </div>
  )
}

export default Signals