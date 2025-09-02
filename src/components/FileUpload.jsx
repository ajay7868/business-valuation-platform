import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-toastify';
import { uploadFile } from '../services/api';

function FileUpload({ onNext, onDataExtracted }) {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    console.log('Files dropped:', acceptedFiles);
    setUploading(true);
    
    for (const file of acceptedFiles) {
      try {
        console.log('Processing file:', file.name, 'Size:', file.size);
        
        // Check file size before uploading (100MB limit)
        const maxSize = 100 * 1024 * 1024; // 100MB
        if (file.size > maxSize) {
          const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
          throw new Error(`File too large: ${sizeMB}MB. Maximum size allowed is 100MB.`);
        }
        
        console.log('Calling uploadFile API...');
        const response = await uploadFile(file);
        console.log('Upload successful, response:', response);
        
        setUploadedFiles(prev => [...prev, {
          name: file.name,
          size: file.size,
          status: 'success',
          data: response.extracted_data
        }]);
        
        // Pass extracted data to parent
        if (response.extracted_data) {
          onDataExtracted(response.extracted_data);
        }
        
        toast.success(`${file.name} uploaded successfully!`);
      } catch (error) {
        console.error('Upload failed for file:', file.name, 'Error:', error);
        setUploadedFiles(prev => [...prev, {
          name: file.name,
          size: file.size,
          status: 'error',
          error: error.message
        }]);
        
        toast.error(`Failed to upload ${file.name}: ${error.message}`);
      }
    }
    
    setUploading(false);
  }, [onDataExtracted]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    multiple: true
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="row">
      <div className="col-md-8">
        <div className="card">
          <div className="card-header">
            <h5>Upload Financial Documents</h5>
            <small className="text-muted">
              Upload P&L statements, balance sheets, tax returns, or CIM documents
            </small>
          </div>
          <div className="card-body">
            <div
              {...getRootProps()}
              className={`upload-zone ${isDragActive ? 'active' : ''}`}
            >
              <input {...getInputProps()} />
              <div className="upload-content">
                <i className="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                <h5>
                  {isDragActive
                    ? 'Drop the files here...'
                    : 'Drag & drop files here, or click to select'}
                </h5>
                <p className="text-muted">
                  Supported formats: PDF, Excel (.xlsx, .xls), CSV<br/>
                  <small>Maximum file size: 100MB</small>
                </p>
                {uploading && (
                  <div className="mt-3">
                    <div className="spinner-border text-primary" role="status">
                      <span className="sr-only">Uploading...</span>
                    </div>
                    <p className="mt-2">Processing files...</p>
                  </div>
                )}
              </div>
            </div>

            {uploadedFiles.length > 0 && (
              <div className="mt-4">
                <h6>Uploaded Files</h6>
                <div className="list-group">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="list-group-item">
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <h6 className="mb-1">{file.name}</h6>
                          <small className="text-muted">
                            {formatFileSize(file.size)}
                          </small>
                        </div>
                        <div>
                          {file.status === 'success' && (
                            <span className="badge badge-success">✓ Uploaded</span>
                          )}
                          {file.status === 'error' && (
                            <span className="badge badge-danger">✗ Error</span>
                          )}
                        </div>
                      </div>
                      {file.error && (
                        <small className="text-danger">{file.error}</small>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="col-md-4">
        <div className="card">
          <div className="card-header">
            <h6>Document Checklist</h6>
          </div>
          <div className="card-body">
            <div className="checklist">
              <div className="form-check">
                <input className="form-check-input" type="checkbox" id="pnl" />
                <label className="form-check-label" htmlFor="pnl">
                  P&L Statements (3-5 years)
                </label>
              </div>
              <div className="form-check">
                <input className="form-check-input" type="checkbox" id="balance" />
                <label className="form-check-label" htmlFor="balance">
                  Balance Sheets (3-5 years)
                </label>
              </div>
              <div className="form-check">
                <input className="form-check-input" type="checkbox" id="tax" />
                <label className="form-check-label" htmlFor="tax">
                  Tax Returns (3-5 years)
                </label>
              </div>
              <div className="form-check">
                <input className="form-check-input" type="checkbox" id="cim" />
                <label className="form-check-label" htmlFor="cim">
                  CIM or Business Summary
                </label>
              </div>
              <div className="form-check">
                <input className="form-check-input" type="checkbox" id="contracts" />
                <label className="form-check-label" htmlFor="contracts">
                  Key Contracts & Leases
                </label>
              </div>
            </div>

            <button
              className="btn btn-primary btn-block mt-3"
              onClick={onNext}
              disabled={uploadedFiles.length === 0}
            >
              Continue to Company Data
            </button>
          </div>
        </div>

        <div className="card mt-3">
          <div className="card-header">
            <h6>Tips</h6>
          </div>
          <div className="card-body">
            <ul className="list-unstyled">
              <li>• Upload clear, readable documents</li>
              <li>• Include 3-5 years of financial data</li>
              <li>• Ensure all pages are included</li>
              <li>• File size limit: 16MB per file</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FileUpload;