import React, { useState, useEffect } from 'react'
import axios from 'axios'
import '../components/HumanReview.css'

const API_BASE = '/api'

function HumanReview() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedReview, setSelectedReview] = useState(null)
  const [decision, setDecision] = useState('')
  const [notes, setNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [reviewerId, setReviewerId] = useState('')
  
  // Generate reviewer ID automatically when review is selected
  const generateReviewerId = () => {
    const timestamp = Date.now()
    const random = Math.random().toString(36).substring(2, 8)
    return `reviewer_${timestamp}_${random}`
  }

  useEffect(() => {
    loadPendingReviews()
    const interval = setInterval(loadPendingReviews, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const loadPendingReviews = async () => {
    try {
      const response = await axios.get(`${API_BASE}/human-review/pending`)
      setReviews(response.data.items)
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDecision = async (checkpointId) => {
    if (!decision) {
      alert('Please select a decision (Accept or Reject)')
      return
    }

    setSubmitting(true)
    try {
      // Auto-generate reviewer ID
      const reviewerId = generateReviewerId()
      
      const response = await axios.post(`${API_BASE}/human-review/decision`, {
        checkpoint_id: checkpointId,
        decision: decision.toUpperCase(),
        notes: notes,
        reviewer_id: reviewerId
      })
      
      if (decision.toUpperCase() === 'ACCEPT') {
        // Show success message and wait for workflow to resume
        alert(`Decision submitted successfully! Reviewer ID: ${reviewerId}\n\nWorkflow is resuming automatically...`)
        
        // Refresh pending reviews after a short delay
        setTimeout(() => {
          loadPendingReviews()
        }, 2000)
      } else {
        alert(`Decision submitted successfully! Reviewer ID: ${reviewerId}`)
      }
      
      setSelectedReview(null)
      setDecision('')
      setNotes('')
      setReviewerId('')
      loadPendingReviews()
    } catch (err) {
      alert(err.response?.data?.detail || err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  if (loading) {
    return <div className="loading">Loading pending reviews...</div>
  }

  return (
    <div className="human-review">
      <div className="card">
        <h2>Human Review Queue</h2>
        
        {error && <div className="error">{error}</div>}
        
        {reviews.length === 0 ? (
          <p>No pending reviews at this time.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Invoice ID</th>
                <th>Vendor</th>
                <th>Amount</th>
                <th>Failed Stage</th>
                <th>Mismatch Reason</th>
                <th>Created At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((review) => (
                <tr key={review.checkpoint_id}>
                  <td>{review.invoice_id}</td>
                  <td>{review.vendor_name}</td>
                  <td>{formatCurrency(review.amount)}</td>
                  <td>
                    <span className="badge badge-danger">{review.failed_stage || 'N/A'}</span>
                  </td>
                  <td>
                    <div style={{ maxWidth: '300px', fontSize: '12px' }}>
                      {review.mismatch_reason || review.reason_for_hold || 'N/A'}
                    </div>
                  </td>
                  <td>{formatDate(review.created_at)}</td>
                  <td>
                    <button
                      className="button button-primary"
                      onClick={() => {
                        setSelectedReview(review)
                        setReviewerId(generateReviewerId()) // Generate ID when review is selected
                      }}
                    >
                      Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {selectedReview && (
        <div className="card review-modal">
          <h3>Review Invoice: {selectedReview.invoice_id}</h3>
          
          <div className="review-details">
            <p><strong>Vendor:</strong> {selectedReview.vendor_name}</p>
            <p><strong>Amount:</strong> {formatCurrency(selectedReview.amount)}</p>
            <p><strong>Failed Stage:</strong> 
              <span className="badge badge-danger" style={{ marginLeft: '10px' }}>
                {selectedReview.failed_stage || 'N/A'}
              </span>
            </p>
            <p><strong>Mismatch Reason:</strong></p>
            <div style={{ 
              backgroundColor: '#fff3cd', 
              border: '1px solid #ffc107', 
              borderRadius: '4px', 
              padding: '10px', 
              marginTop: '5px',
              fontSize: '14px',
              lineHeight: '1.5'
            }}>
              {selectedReview.mismatch_reason || selectedReview.reason_for_hold || 'No detailed reason available'}
            </div>
            <p style={{ marginTop: '10px' }}><strong>Created:</strong> {formatDate(selectedReview.created_at)}</p>
          </div>

          <div className="review-form">
            <div className="form-group">
              <label className="label">Decision *</label>
              <select
                className="input"
                value={decision}
                onChange={(e) => setDecision(e.target.value)}
              >
                <option value="">Select decision</option>
                <option value="ACCEPT">Accept</option>
                <option value="REJECT">Reject</option>
              </select>
            </div>

            <div className="form-group">
              <label className="label">Reviewer ID</label>
              <input
                type="text"
                className="input"
                value={reviewerId || generateReviewerId()}
                readOnly
                disabled
                placeholder="Auto-generated"
                style={{ backgroundColor: '#f5f5f5', color: '#666' }}
              />
              <small style={{ color: '#666', fontSize: '12px' }}>Reviewer ID is automatically generated</small>
            </div>

            <div className="form-group">
              <label className="label">Notes</label>
              <textarea
                className="input"
                rows="4"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add any notes about your decision..."
              />
            </div>

            <div className="review-actions">
              <button
                className="button button-success"
                onClick={() => handleDecision(selectedReview.checkpoint_id)}
                disabled={submitting || !decision}
              >
                {submitting ? 'Submitting...' : 'Submit Decision'}
              </button>
              <button
                className="button"
                onClick={() => {
                  setSelectedReview(null)
                  setDecision('')
                  setNotes('')
                  setReviewerId('')
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default HumanReview

