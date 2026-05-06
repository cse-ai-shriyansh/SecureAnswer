import { useState, useRef } from 'react'
import useSWR from 'swr'
import { fetchIngestion, uploadFile } from '../lib/api'
import Card from '../components/Card'
import StatCard from '../components/StatCard'
import Badge from '../components/Badge'
import Button from '../components/Button'
import Modal from '../components/Modal'
import DataTable from '../components/DataTable'
import { Upload, FileText, CheckCircle, AlertCircle, Clock, File } from 'lucide-react'

export default function Ingestion() {
  const [dragActive, setDragActive] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef(null)

  const { data, error, mutate } = useSWR('/ingestion', fetchIngestion, { refreshInterval: 7000 })

  const stats = data?.stats || []
  const files = data?.files || []

  const columns = [
    { key: 'name', label: 'File Name', render: (val) => <span className="font-medium">{val}</span> },
    { key: 'size', label: 'Size' },
    { key: 'type', label: 'Type' },
    {
      key: 'status',
      label: 'Status',
      render: (val) => (
        <Badge variant={val === 'completed' ? 'success' : 'warning'}>
          {val}
        </Badge>
      ),
    },
    { key: 'documents', label: 'Documents' },
    { key: 'uploadedAt', label: 'Uploaded' },
    {
      key: 'id',
      label: 'Action',
      render: () => <Button variant="ghost" size="sm">View</Button>,
    },
  ]

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    // Extract files from drop event and handle them
    const files = e.dataTransfer?.files
    if (files && files.length) {
      handleFiles(files)
    }
  }

  const handleFiles = async (fileList) => {
    try {
      setIsUploading(true)
      // Upload each file individually
      for (const f of Array.from(fileList)) {
        const form = new FormData()
        form.append('file', f)
        const result = await uploadFile(form)
        console.log(`Uploaded ${f.name}:`, result)
      }
      // Refresh the file list after all uploads
      mutate()
      setShowUploadModal(false)
      setSelectedFiles([])
    } catch (err) {
      console.error('Upload failed:', err)
    } finally {
      setIsUploading(false)
    }
  }

  // file input change - just select files, don't upload yet
  const onInputChange = (e) => {
    const files = e.target.files
    if (files && files.length) {
      setSelectedFiles(Array.from(files))
    }
  }

  // Upload button handler
  const handleUploadClick = () => {
    if (selectedFiles.length === 0) {
      // If no files selected, open file chooser
      fileInputRef.current?.click()
    } else {
      // If files selected, start upload
      handleFiles(selectedFiles)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-text-primary mb-2">Document Ingestion</h1>
        <p className="text-text-secondary">Upload and manage documents for your knowledge base.</p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat, idx) => (
          <StatCard
            key={idx}
            icon={stat.icon}
            label={stat.label}
            value={stat.value}
            change={stat.change}
            changeType={stat.changeType}
            footer={stat.footer}
          />
        ))}
      </div>

      {/* Upload Area */}
      <Card
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`transition-smooth cursor-pointer ${
          dragActive ? 'border-primary border-2 bg-secondary' : ''
        }`}
      >
        <div className="py-16 text-center">
          <div className="flex justify-center mb-4">
            <div className="w-20 h-20 rounded-full bg-secondary flex items-center justify-center">
              <Upload className="text-primary" size={40} />
            </div>
          </div>
          <h3 className="text-xl font-semibold text-text-primary mb-2">Drop files here to upload</h3>
          <p className="text-text-secondary mb-6">
            or{' '}
            <button
              onClick={() => setShowUploadModal(true)}
              className="text-primary hover:text-accent font-semibold transition-smooth"
            >
              browse files
            </button>
          </p>
          <p className="text-xs text-text-tertiary">
            Supports PDF, Word, Excel, PPT, TXT (max 100 MB each)
          </p>
        </div>
      </Card>

      {/* File Processing Status */}
      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">File Processing Status</h3>
        <DataTable columns={columns} data={files} sortable={true} />
      </div>

      {/* Upload Modal */}
      <Modal
        isOpen={showUploadModal}
        onClose={() => {
          setShowUploadModal(false)
          setSelectedFiles([])
        }}
        title="Upload Documents"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-text-secondary">
            Select one or more files to upload. Each file can be up to 100 MB.
          </p>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="w-full"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt"
            onChange={onInputChange}
          />
          {selectedFiles.length > 0 && (
            <div className="bg-secondary p-3 rounded-md">
              <p className="text-sm font-medium text-text-primary mb-2">Selected files:</p>
              <ul className="text-xs text-text-secondary space-y-1">
                {selectedFiles.map((f, idx) => (
                  <li key={idx}>• {f.name} ({(f.size / 1024 / 1024).toFixed(2)} MB)</li>
                ))}
              </ul>
            </div>
          )}
          <div className="flex justify-end gap-3">
            <Button 
              variant="secondary" 
              onClick={() => {
                setShowUploadModal(false)
                setSelectedFiles([])
              }}
            >
              Cancel
            </Button>
            <Button 
              variant="primary" 
              onClick={handleUploadClick}
              disabled={isUploading}
            >
              {isUploading ? 'Uploading...' : selectedFiles.length > 0 ? 'Upload' : 'Choose Files'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
