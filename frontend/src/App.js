import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const API_URL = process.env.NODE_ENV === 'production' ? 'https://safdar1.pythonanywhere.com' : 'http://localhost:5000';

function App() {
  const [formData, setFormData] = useState({
    client_name: '',
    client_address: '',
    client_gstin: '',
    invoice_number: '',
    invoice_date: '',
    items: [{ description: '', hsn_code: '', quantity: 0, rate: 0 }],
    gst_percentage: 18,
    transport_charge: 0,
    advance_payment: 0,
    minimum_quantity: '',
    delivery_time: '',
    payment_terms: '',
  });
  const [templateFile, setTemplateFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState('');
  const [pdfUrl, setPdfUrl] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [geminiApiKey, setGeminiApiKey] = useState('');

  const handleChange = (e, index) => {
    const { name, value } = e.target;
    if (e.target.dataset.name) {
      const newItems = [...formData.items];
      newItems[index][e.target.dataset.name] = value;
      setFormData({ ...formData, items: newItems });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleAddItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { description: '', hsn_code: '', quantity: 0, rate: 0 }],
    });
  };

  const handleFileChange = (e) => {
    setTemplateFile(e.target.files[0]);
  };

  const handleTemplateUpload = async () => {
    if (!templateFile) {
      setUploadMessage('Please select a file to upload.');
      return;
    }
    const uploadData = new FormData();
    uploadData.append('file', templateFile);

    const response = await fetch(`${API_URL}/upload_template`, {
      method: 'POST',
      body: uploadData,
    });
    const data = await response.json();
    setUploadMessage(data.message);
  };

  const generatePdf = async (isInvoice) => {
    const payload = { ...formData };
    if (!isInvoice) {
        payload.invoice_number = null;
        payload.invoice_date = null;
    }

    const response = await fetch(`${API_URL}/generate_pdf`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ form_data: payload, api_key: geminiApiKey }),
    });

    if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        setPdfUrl(url);
    } else {
        console.error("Failed to generate PDF");
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    const newChatHistory = [...chatHistory, { role: 'user', content: chatInput }];
    setChatHistory(newChatHistory);

    const response = await fetch(`${API_URL}/chatbot`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command: chatInput, form_data: formData, api_key: geminiApiKey }),
    });

    const data = await response.json();
    setFormData(data.form_data);
    setChatHistory([...newChatHistory, { role: 'assistant', content: data.chatbot_response }]);
    setChatInput('');

    // Regenerate the PDF with the updated form data
    const isInvoice = !!data.form_data.invoice_number;
    generatePdf(isInvoice, data.form_data);
  };


  return (
    <div className="container-fluid mt-5">
        <div className="row">
            <div className="col-md-5">
                <h1>Invoice and Quotation Generator</h1>

                <div className="card mb-4">
                    <div className="card-body">
                        <h5 className="card-title">Enter Your Gemini API Key</h5>
                        <div className="form-group">
                            <input type="text" className="form-control" placeholder="Gemini API Key" value={geminiApiKey} onChange={(e) => setGeminiApiKey(e.target.value)} />
                        </div>
                    </div>
                </div>

                <div className="card mb-4">
                    <div className="card-body">
                        <h5 className="card-title">Upload Letterhead Template</h5>
                        <div className="form-group">
                            <input type="file" className="form-control-file" onChange={handleFileChange} />
                        </div>
                        <button type="button" className="btn btn-info" onClick={handleTemplateUpload}>
                            Upload Template
                        </button>
                        {uploadMessage && <p className="mt-2">{uploadMessage}</p>}
                    </div>
                </div>

                <form>
                    {/* Form fields remain the same as before */}
                    <div className="form-group">
          <label>Client Name</label>
          <input
            type="text"
            className="form-control"
            name="client_name"
            value={formData.client_name}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Client Address</label>
          <input
            type="text"
            className="form-control"
            name="client_address"
            value={formData.client_address}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Client GSTIN</label>
          <input
            type="text"
            className="form-control"
            name="client_gstin"
            value={formData.client_gstin}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Invoice Number</label>
          <input
            type="text"
            className="form-control"
            name="invoice_number"
            value={formData.invoice_number}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Invoice Date</label>
          <input
            type="date"
            className="form-control"
            name="invoice_date"
            value={formData.invoice_date}
            onChange={handleChange}
          />
        </div>

        <hr />

        <h3>Items</h3>
        {formData.items.map((item, index) => (
          <div key={index} className="form-row">
            <div className="form-group col-md-5">
              <label>Description</label>
              <input
                type="text"
                className="form-control"
                data-name="description"
                value={item.description}
                onChange={(e) => handleChange(e, index)}
              />
            </div>
            <div className="form-group col-md-3">
              <label>HSN Code</label>
              <input
                type="text"
                className="form-control"
                data-name="hsn_code"
                value={item.hsn_code}
                onChange={(e) => handleChange(e, index)}
              />
            </div>
            <div className="form-group col-md-2">
              <label>Quantity</label>
              <input
                type="number"
                className="form-control"
                data-name="quantity"
                value={item.quantity}
                onChange={(e) => handleChange(e, index)}
              />
            </div>
            <div className="form-group col-md-2">
              <label>Rate</label>
              <input
                type="number"
                className="form-control"
                data-name="rate"
                value={item.rate}
                onChange={(e) => handleChange(e, index)}
              />
            </div>
          </div>
        ))}
        <button type="button" className="btn btn-primary" onClick={handleAddItem}>
          Add Item
        </button>

        <hr />

        <div className="form-group">
          <label>GST Percentage</label>
          <input
            type="number"
            className="form-control"
            name="gst_percentage"
            value={formData.gst_percentage}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Transport Charge</label>
          <input
            type="number"
            className="form-control"
            name="transport_charge"
            value={formData.transport_charge}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Advance Payment</label>
          <input
            type="number"
            className="form-control"
            name="advance_payment"
            value={formData.advance_payment}
            onChange={handleChange}
          />
        </div>

        <hr />

        <h3>Quotation Specific</h3>
        <div className="form-group">
          <label>Minimum Quantity</label>
          <input
            type="text"
            className="form-control"
            name="minimum_quantity"
            value={formData.minimum_quantity}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Delivery Time</label>
          <input
            type="text"
            className="form-control"
            name="delivery_time"
            value={formData.delivery_time}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Payment Terms</label>
          <input
            type="text"
            className="form-control"
            name="payment_terms"
            value={formData.payment_terms}
            onChange={handleChange}
          />
        </div>

                    <div className="mb-5">
                        <button type="button" className="btn btn-success mr-2" onClick={() => generatePdf(true)}>
                            Generate Invoice
                        </button>
                        <button type="button" className="btn btn-warning" onClick={() => generatePdf(false)}>
                            Generate Quotation
                        </button>
                    </div>
                </form>
            </div>
            <div className="col-md-7">
                <div className="pdf-viewer">
                    <h2>PDF Preview</h2>
                    {pdfUrl ? (
                        <div>
                            <iframe src={pdfUrl} width="100%" height="600px" title="pdf-preview"></iframe>
                            <a href={pdfUrl} download="generated_document.pdf" className="btn btn-primary mt-2">Download PDF</a>
                        </div>
                    ) : (
                        <div className="border p-5 text-center">Preview will appear here</div>
                    )}
                </div>
                <div className="chatbot mt-4">
                    <h2>Chatbot</h2>
                    <div className="chat-history border p-3" style={{height: "300px", overflowY: "scroll"}}>
                        {chatHistory.map((message, index) => (
                            <div key={index} className={`text-${message.role === 'user' ? 'right' : 'left'}`}>
                                <strong>{message.role}:</strong> {message.content}
                            </div>
                        ))}
                    </div>
                    <form onSubmit={handleChatSubmit} className="mt-2">
                        <div className="input-group">
                            <input 
                                type="text" 
                                className="form-control" 
                                value={chatInput} 
                                onChange={(e) => setChatInput(e.target.value)} 
                                placeholder="Type your command..." 
                            />
                            <div className="input-group-append">
                                <button type="submit" className="btn btn-primary">Send</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
  );
}

export default App;