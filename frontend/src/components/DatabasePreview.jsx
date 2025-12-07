import React, { useState, useEffect } from 'react'
import axios from 'axios'
import '../components/DatabasePreview.css'

const API_BASE = '/api'

function DatabasePreview() {
  const [workflows, setWorkflows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedWorkflow, setSelectedWorkflow] = useState(null)
  const [filter, setFilter] = useState('all') // all, pending, accepted, rejected, completed
  const [sortBy, setSortBy] = useState('created_at') // created_at, amount, vendor_name, invoice_id, status
  const [sortOrder, setSortOrder] = useState('desc') // asc, desc
  const [deleting, setDeleting] = useState(null) // thread_id being deleted

  useEffect(() => {
    loadWorkflows()
    const interval = setInterval(loadWorkflows, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const loadWorkflows = async () => {
    try {
      const response = await axios.get(`${API_BASE}/workflow/all`)
      setWorkflows(response.data.workflows || [])
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const deleteWorkflow = async (threadId, invoiceId) => {
    if (!window.confirm(`Are you sure you want to delete invoice ${invoiceId}? This action cannot be undone.`)) {
      return
    }

    setDeleting(threadId)
    try {
      await axios.delete(`${API_BASE}/workflow/${threadId}`)
      setError(null)
      // Reload workflows after deletion
      await loadWorkflows()
      if (selectedWorkflow && selectedWorkflow.thread_id === threadId) {
        setSelectedWorkflow(null)
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to delete workflow')
    } finally {
      setDeleting(null)
    }
  }

  const handleSort = (field) => {
    if (sortBy === field) {
      // Toggle sort order
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('desc')
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  const getStatusBadge = (status, decision) => {
    if (status === 'COMPLETED') return <span className="badge badge-success">Completed</span>
    if (status === 'PAUSED') return <span className="badge badge-warning">Paused</span>
    if (decision === 'ACCEPT') return <span className="badge badge-success">Accepted</span>
    if (decision === 'REJECT') return <span className="badge badge-danger">Rejected</span>
    if (status === 'REQUIRES_MANUAL_HANDLING') return <span className="badge badge-danger">Manual Handling</span>
    return <span className="badge badge-info">{status || 'Unknown'}</span>
  }

  const filteredWorkflows = workflows.filter(w => {
    if (filter === 'all') return true
    if (filter === 'pending') {
      // Only show as pending if:
      // - Status is PAUSED (workflow is actually paused)
      // - No decision yet (not accepted/rejected)
      // - Not completed
      return w.status === 'PAUSED' && !w.decision && w.status !== 'COMPLETED'
    }
    if (filter === 'accepted') {
      // Show only workflows where human made ACCEPT decision (HITL decision: ACCEPT)
      // These are workflows that went through HITL and were accepted by human
      return w.decision === 'ACCEPT'
    }
    if (filter === 'rejected') {
      // Show workflows where human made REJECT decision (HITL decision: REJECT)
      return w.decision === 'REJECT'
    }
    if (filter === 'completed') {
      // Show ALL completed workflows (with or without HITL)
      // This includes:
      // - Auto-completed workflows (never hit HITL)
      // - Human-accepted workflows (went through HITL, decision: ACCEPT)
      // - Human-rejected workflows (went through HITL, decision: REJECT)
      return w.status === 'COMPLETED'
    }
    return true
  })

  // Sort filtered workflows
  const sortedWorkflows = [...filteredWorkflows].sort((a, b) => {
    let aVal, bVal
    
    switch (sortBy) {
      case 'created_at':
        aVal = a.created_at ? new Date(a.created_at).getTime() : 0
        bVal = b.created_at ? new Date(b.created_at).getTime() : 0
        break
      case 'amount':
        aVal = a.amount || 0
        bVal = b.amount || 0
        break
      case 'vendor_name':
        aVal = (a.vendor_name || '').toLowerCase()
        bVal = (b.vendor_name || '').toLowerCase()
        break
      case 'invoice_id':
        aVal = (a.invoice_id || '').toLowerCase()
        bVal = (b.invoice_id || '').toLowerCase()
        break
      case 'status':
        aVal = (a.status || '').toLowerCase()
        bVal = (b.status || '').toLowerCase()
        break
      default:
        return 0
    }
    
    if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1
    if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1
    return 0
  })
  
  // Calculate accurate counts for tabs
  const pendingCount = workflows.filter(w => w.status === 'PAUSED' && !w.decision && w.status !== 'COMPLETED').length
  // Accepted = total jobs where human accepted the flow (HITL decision: ACCEPT)
  // Note: These are a subset of completed workflows
  const acceptedCount = workflows.filter(w => w.decision === 'ACCEPT').length
  // Rejected = workflows where human made REJECT decision
  const rejectedCount = workflows.filter(w => w.decision === 'REJECT').length
  // Completed = ALL completed workflows (with or without HITL)
  // Includes: auto-completed, human-accepted, and human-rejected
  const completedCount = workflows.filter(w => w.status === 'COMPLETED').length

  if (loading) {
    return <div className="loading">Loading workflows from database...</div>
  }

  return (
    <div className="database-preview">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>Database Preview - All Invoices</h2>
          <div>
            <button onClick={loadWorkflows} className="button button-primary" style={{ marginRight: '10px' }}>
              Refresh
            </button>
            <span style={{ marginRight: '10px', fontWeight: '500' }}>Total: {workflows.length}</span>
          </div>
        </div>

        {error && <div className="error">{error}</div>}

        {/* Filters and Sorting */}
        <div style={{ marginBottom: '20px' }}>
          {/* Filters */}
          <div className="filters" style={{ marginBottom: '15px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            className={`button ${filter === 'all' ? 'button-primary' : ''}`}
            onClick={() => setFilter('all')}
          >
            All ({workflows.length})
          </button>
          <button
            className={`button ${filter === 'pending' ? 'button-primary' : ''}`}
            onClick={() => setFilter('pending')}
          >
            Pending ({pendingCount})
          </button>
          <button
            className={`button ${filter === 'accepted' ? 'button-primary' : ''}`}
            onClick={() => setFilter('accepted')}
            title="Workflows where human accepted (HITL decision: ACCEPT)"
          >
            Accepted ({acceptedCount})
          </button>
          <button
            className={`button ${filter === 'rejected' ? 'button-primary' : ''}`}
            onClick={() => setFilter('rejected')}
            title="Workflows where human rejected (HITL decision: REJECT)"
          >
            Rejected ({rejectedCount})
          </button>
          <button
            className={`button ${filter === 'completed' ? 'button-primary' : ''}`}
            onClick={() => setFilter('completed')}
            title="All completed workflows (includes auto-completed and human-accepted/rejected)"
          >
            Completed ({completedCount})
          </button>
          </div>

          {/* Sorting */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <span style={{ fontWeight: '500' }}>Sort by:</span>
            {['created_at', 'amount', 'vendor_name', 'invoice_id', 'status'].map(field => (
              <button
                key={field}
                className={`button ${sortBy === field ? 'button-primary' : ''}`}
                onClick={() => handleSort(field)}
                style={{ fontSize: '0.9em', padding: '5px 10px' }}
              >
                {field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                {sortBy === field && (
                  <span style={{ marginLeft: '5px' }}>
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {sortedWorkflows.length === 0 ? (
          <p>No workflows found.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Invoice ID</th>
                <th>Vendor</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Decision</th>
                <th>Current Stage</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedWorkflows.map((workflow) => (
                <tr key={workflow.checkpoint_id || workflow.thread_id}>
                  <td>{workflow.invoice_id || 'N/A'}</td>
                  <td>{workflow.vendor_name || 'N/A'}</td>
                  <td>{workflow.amount ? formatCurrency(workflow.amount) : 'N/A'}</td>
                  <td>{getStatusBadge(workflow.status, workflow.decision)}</td>
                  <td>
                    {workflow.decision ? (
                      <span className={`badge ${workflow.decision === 'ACCEPT' ? 'badge-success' : 'badge-danger'}`}>
                        {workflow.decision}
                      </span>
                    ) : workflow.status === 'COMPLETED' && workflow.went_through_hitl ? (
                      <span className="badge badge-warning">Completed (Decision Missing)</span>
                    ) : workflow.status === 'COMPLETED' && workflow.reason_for_hold ? (
                      <span className="badge badge-warning">Completed (Decision Missing)</span>
                    ) : workflow.status === 'COMPLETED' ? (
                      <span className="badge badge-success">Completed (No Review Needed)</span>
                    ) : workflow.status === 'PAUSED' ? (
                      <span className="badge badge-info">Pending Review</span>
                    ) : (
                      <span className="badge badge-info">Pending</span>
                    )}
                  </td>
                  <td>{workflow.current_stage || 'N/A'}</td>
                  <td>{formatDate(workflow.created_at)}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '5px' }}>
                      <button
                        className="button button-primary"
                        onClick={() => setSelectedWorkflow(workflow)}
                      >
                        View Details
                      </button>
                      <button
                        className="button"
                        style={{ backgroundColor: '#dc3545', color: 'white' }}
                        onClick={() => deleteWorkflow(workflow.thread_id, workflow.invoice_id)}
                        disabled={deleting === workflow.thread_id}
                        title="Delete this workflow"
                      >
                        {deleting === workflow.thread_id ? 'Deleting...' : 'Delete'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Detail Modal */}
      {selectedWorkflow && (
        <div className="card detail-modal">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3>Invoice Details: {selectedWorkflow.invoice_id}</h3>
            <button
              className="button"
              onClick={() => setSelectedWorkflow(null)}
            >
              Close
            </button>
          </div>

          <div className="detail-sections">
            <div className="detail-section">
              <h4>Basic Information</h4>
              <div className="detail-grid">
                <div><strong>Invoice ID:</strong> {selectedWorkflow.invoice_id}</div>
                <div><strong>Thread ID:</strong> {selectedWorkflow.thread_id}</div>
                <div><strong>Checkpoint ID:</strong> {selectedWorkflow.checkpoint_id}</div>
                <div><strong>Vendor:</strong> {selectedWorkflow.vendor_name}</div>
                <div><strong>Amount:</strong> {selectedWorkflow.amount ? formatCurrency(selectedWorkflow.amount) : 'N/A'}</div>
                <div><strong>Status:</strong> {selectedWorkflow.status}</div>
                <div><strong>Current Stage:</strong> {selectedWorkflow.current_stage || 'N/A'}</div>
                <div><strong>Paused:</strong> {selectedWorkflow.paused ? 'Yes' : 'No'}</div>
              </div>
            </div>

            {selectedWorkflow.decision && (
              <div className="detail-section">
                <h4>Human Review Decision</h4>
                <div className="detail-grid">
                  <div><strong>Decision:</strong> {selectedWorkflow.decision}</div>
                  <div><strong>Reviewer ID:</strong> {selectedWorkflow.reviewer_id || 'N/A'}</div>
                  <div><strong>Reason for Hold:</strong> {selectedWorkflow.reason_for_hold || 'N/A'}</div>
                  <div><strong>Notes:</strong> {selectedWorkflow.notes || 'None'}</div>
                  <div><strong>Reviewed At:</strong> {formatDate(selectedWorkflow.updated_at)}</div>
                </div>
              </div>
            )}

            {selectedWorkflow.invoice_payload && (
              <div className="detail-section">
                <h4>Invoice Payload</h4>
                <pre className="json-viewer">
                  {JSON.stringify(selectedWorkflow.invoice_payload, null, 2)}
                </pre>
              </div>
            )}

            {selectedWorkflow.stages && (
              <div className="detail-section">
                <h4>Workflow Stages</h4>
                <div className="stages-list">
                  {Object.entries(selectedWorkflow.stages).map(([stageName, stageData]) => (
                    stageData && (
                      <div key={stageName} className="stage-item">
                        <strong>{stageName.toUpperCase()}:</strong>
                        <pre className="json-viewer-small">
                          {JSON.stringify(stageData, null, 2)}
                        </pre>
                      </div>
                    )
                  ))}
                </div>
              </div>
            )}

            <div className="detail-section">
              <h4>Timestamps</h4>
              <div className="detail-grid">
                <div><strong>Created:</strong> {formatDate(selectedWorkflow.created_at)}</div>
                {selectedWorkflow.updated_at && (
                  <div><strong>Updated:</strong> {formatDate(selectedWorkflow.updated_at)}</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DatabasePreview

