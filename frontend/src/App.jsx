import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import InvoiceSubmit from './components/InvoiceSubmit'
import HumanReview from './components/HumanReview'
import DatabasePreview from './components/DatabasePreview'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="container">
            <h1>🧾 Langie - Invoice Processing Agent</h1>
            <div className="nav-links">
              <Link to="/">Submit Invoice</Link>
              <Link to="/review">Human Review</Link>
              <Link to="/database">Database Preview</Link>
            </div>
          </div>
        </nav>
        <div className="container">
          <Routes>
            <Route path="/" element={<InvoiceSubmit />} />
            <Route path="/review" element={<HumanReview />} />
            <Route path="/database" element={<DatabasePreview />} />
          </Routes>
        </div>
      </div>
    </Router>
  )
}

export default App

