import React, { useState } from 'react'
import axios from 'axios'
import '../components/InvoiceSubmit.css'

const API_BASE = '/api'

function InvoiceSubmit() {
  const [formData, setFormData] = useState({
    invoice_id: '',
    vendor_name: '',
    vendor_tax_id: '',
    invoice_date: '',
    due_date: '',
    amount: '',
    currency: 'USD',
    line_items: [{ desc: '', qty: '', unit_price: '', total: '' }],
    attachments: []
  })
  const [uploadedFiles, setUploadedFiles] = useState([])
  
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleLineItemChange = (index, field, value) => {
    const newLineItems = [...formData.line_items]
    newLineItems[index][field] = value
    
    // Auto-calculate total
    if (field === 'qty' || field === 'unit_price') {
      const qty = parseFloat(newLineItems[index].qty) || 0
      const price = parseFloat(newLineItems[index].unit_price) || 0
      newLineItems[index].total = (qty * price).toFixed(2)
    }
    
    setFormData(prev => ({
      ...prev,
      line_items: newLineItems
    }))
  }

  const addLineItem = () => {
    setFormData(prev => ({
      ...prev,
      line_items: [...prev.line_items, { desc: '', qty: '', unit_price: '', total: '' }]
    }))
  }

  const removeLineItem = (index) => {
    setFormData(prev => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index)
    }))
  }

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files)
    setUploadedFiles(files)
    
    // Update formData with file names (for now, backend will handle actual uploads)
    setFormData(prev => ({
      ...prev,
      attachments: files.map(f => f.name)
    }))
  }

  const handleRemoveFile = (index) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index)
    setUploadedFiles(newFiles)
    setFormData(prev => ({
      ...prev,
      attachments: newFiles.map(f => f.name)
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // Create FormData for file uploads
      const formDataToSend = new FormData()
      
      // Add invoice data as JSON
      const invoiceData = {
        ...formData,
        amount: parseFloat(formData.amount),
        line_items: formData.line_items.map(item => ({
          desc: item.desc,
          qty: parseFloat(item.qty) || 0,
          unit_price: parseFloat(item.unit_price) || 0,
          total: parseFloat(item.total) || 0
        })),
        attachments: uploadedFiles.map(f => f.name) // File names for reference
      }
      
      formDataToSend.append('invoice', JSON.stringify(invoiceData))
      
      // Add files
      uploadedFiles.forEach((file, index) => {
        formDataToSend.append(`file_${index}`, file)
      })
      
      formDataToSend.append('file_count', uploadedFiles.length.toString())

      const response = await axios.post(
        `${API_BASE}/workflow/run`,
        formDataToSend,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      setResult(response.data)
      
      if (response.data.status === 'PAUSED') {
        // Redirect to review page after a moment
        setTimeout(() => {
          window.location.href = '/review'
        }, 2000)
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="invoice-submit">
      <div className="card">
        <h2>Submit Invoice for Processing</h2>
        
        {error && <div className="error">{error}</div>}
        
        {result && (
          <div className={`message ${result.status === 'PAUSED' ? 'success' : 'info'}`}>
            <h3>Workflow {result.status}</h3>
            <p>{result.message}</p>
            {result.thread_id && <p><strong>Thread ID:</strong> {result.thread_id}</p>}
            {result.checkpoint_id && <p><strong>Checkpoint ID:</strong> {result.checkpoint_id}</p>}
            {result.review_url && <p><a href={result.review_url}>Review Invoice</a></p>}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label className="label">Invoice ID *</label>
              <input
                type="text"
                name="invoice_id"
                className="input"
                value={formData.invoice_id}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label className="label">Vendor Name *</label>
              <input
                type="text"
                name="vendor_name"
                className="input"
                value={formData.vendor_name}
                onChange={handleInputChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="label">Vendor Tax ID</label>
              <input
                type="text"
                name="vendor_tax_id"
                className="input"
                value={formData.vendor_tax_id}
                onChange={handleInputChange}
              />
            </div>
            <div className="form-group">
              <label className="label">Currency</label>
              <select
                name="currency"
                className="input"
                value={formData.currency}
                onChange={handleInputChange}
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="label">Invoice Date *</label>
              <input
                type="date"
                name="invoice_date"
                className="input"
                value={formData.invoice_date}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label className="label">Due Date *</label>
              <input
                type="date"
                name="due_date"
                className="input"
                value={formData.due_date}
                onChange={handleInputChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="label">Total Amount *</label>
            <input
              type="number"
              name="amount"
              className="input"
              step="0.01"
              value={formData.amount}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="label">Invoice Attachments (PDF/Images)</label>
            <input
              type="file"
              className="input"
              multiple
              accept=".pdf,.png,.jpg,.jpeg,.jpe,.bmp,.tiff,.tif"
              onChange={handleFileChange}
            />
            {uploadedFiles.length > 0 && (
              <div className="uploaded-files" style={{ marginTop: '10px' }}>
                <strong>Selected Files:</strong>
                <ul style={{ listStyle: 'none', padding: 0, marginTop: '5px' }}>
                  {uploadedFiles.map((file, index) => (
                    <li key={index} style={{ 
                      padding: '5px', 
                      background: '#f0f0f0', 
                      marginBottom: '5px',
                      borderRadius: '4px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <span>{file.name} ({(file.size / 1024).toFixed(2)} KB)</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveFile(index)}
                        className="button button-danger"
                        style={{ padding: '5px 10px', fontSize: '12px' }}
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <small style={{ color: '#666', fontSize: '12px', display: 'block', marginTop: '5px' }}>
              Upload PDF invoices or images (PNG, JPG, JPEG, BMP, TIFF) for OCR processing. 
              PDFs use text extraction, images use Tesseract OCR. Files will be parsed automatically.
            </small>
          </div>

          <div className="form-group">
            <label className="label">Line Items *</label>
            {formData.line_items.map((item, index) => (
              <div key={index} className="line-item">
                <input
                  type="text"
                  placeholder="Description"
                  className="input"
                  value={item.desc}
                  onChange={(e) => handleLineItemChange(index, 'desc', e.target.value)}
                  required
                />
                <input
                  type="number"
                  placeholder="Quantity"
                  className="input"
                  step="0.01"
                  value={item.qty}
                  onChange={(e) => handleLineItemChange(index, 'qty', e.target.value)}
                  required
                />
                <input
                  type="number"
                  placeholder="Unit Price"
                  className="input"
                  step="0.01"
                  value={item.unit_price}
                  onChange={(e) => handleLineItemChange(index, 'unit_price', e.target.value)}
                  required
                />
                <input
                  type="number"
                  placeholder="Total"
                  className="input"
                  value={item.total}
                  readOnly
                />
                {formData.line_items.length > 1 && (
                  <button
                    type="button"
                    className="button button-danger"
                    onClick={() => removeLineItem(index)}
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              className="button button-primary"
              onClick={addLineItem}
            >
              Add Line Item
            </button>
          </div>

          <button
            type="submit"
            className="button button-primary"
            disabled={loading}
          >
            {loading ? 'Processing...' : 'Submit Invoice'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default InvoiceSubmit

