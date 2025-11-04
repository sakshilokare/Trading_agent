import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Dashboard from './Dashboard'
import Portfolio from './Portfolio'
import TradingChart from './TradingChart'
import Signals from './Signals'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [agentStatus, setAgentStatus] = useState('inactive')

  useEffect(() => {
    checkAgentStatus()
  }, [])

  const checkAgentStatus = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/agent/status')
      setAgentStatus(response.data.status)
    } catch (error) {
      console.error('Error checking agent status:', error)
    }
  }

  const startAgent = async () => {
    try {
      await axios.post('http://localhost:5000/api/agent/start', {
        symbols: ['AAPL', 'MSFT', 'GOOGL', 'TSLA'],
        initial_capital: 10000
      })
      setAgentStatus('active')
      alert('Trading agent started successfully!')
    } catch (error) {
      alert('Error starting agent: ' + (error.response?.data?.message || error.message))
    }
  }

  const stopAgent = async () => {
    try {
      await axios.post('http://localhost:5000/api/agent/stop')
      setAgentStatus('inactive')
      alert('Trading agent stopped!')
    } catch (error) {
      alert('Error stopping agent: ' + (error.response?.data?.message || error.message))
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Trading Agent</h1>
        <div className="agent-controls">
          <span className={`status ${agentStatus}`}>
            Status: {agentStatus.toUpperCase()}
          </span>
          {agentStatus === 'inactive' ? (
            <button onClick={startAgent} className="btn btn-start">
              Start Agent
            </button>
          ) : (
            <button onClick={stopAgent} className="btn btn-stop">
              Stop Agent
            </button>
          )}
        </div>
      </header>

      <nav className="tabs">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={activeTab === 'portfolio' ? 'active' : ''}
          onClick={() => setActiveTab('portfolio')}
        >
          Portfolio
        </button>
        <button 
          className={activeTab === 'charts' ? 'active' : ''}
          onClick={() => setActiveTab('charts')}
        >
          Charts
        </button>
        <button 
          className={activeTab === 'signals' ? 'active' : ''}
          onClick={() => setActiveTab('signals')}
        >
          Trading Signals
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'portfolio' && <Portfolio />}
        {activeTab === 'charts' && <TradingChart />}
        {activeTab === 'signals' && <Signals />}
      </main>
    </div>
  )
}

export default App