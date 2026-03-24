import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Upload, FileText, Trash2, Clock, Search, X, File, FileType, Moon, Sun, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import { listFiles, uploadFile, deleteFile, getDepartment } from '../services/api'
import { formatDistanceToNow, format, isToday, isYesterday, isThisWeek } from 'date-fns'
import { useTheme } from '../contexts/ThemeContext'
import './DocumentsPage.css'

const DocumentsPage = () => {
  const { departmentCode } = useParams()
  const navigate = useNavigate()
  const { theme, toggleTheme } = useTheme()
  const [department, setDepartment] = useState(null)
  const [files, setFiles] = useState([])
  const [filteredFiles, setFilteredFiles] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [uploading, setUploading] = useState(false)
  const [deleting, setDeleting] = useState({})
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)
  const dropZoneRef = useRef(null)

  useEffect(() => {
    loadDepartment()
    loadFiles()
  }, [departmentCode])

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredFiles(files)
    } else {
      const filtered = files.filter(file =>
        file.original_filename?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        file.filename?.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setFilteredFiles(filtered)
    }
  }, [searchQuery, files])

  const loadDepartment = async () => {
    try {
      const dept = await getDepartment(departmentCode)
      setDepartment(dept)
    } catch (error) {
      console.error('Error loading department:', error)
      setDepartment({ 
        code: departmentCode, 
        name: departmentCode.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) 
      })
    }
  }

  const loadFiles = async () => {
    try {
      const data = await listFiles(departmentCode)
      setFiles(data.files || [])
      setFilteredFiles(data.files || [])
    } catch (error) {
      console.error('Error loading files:', error)
    }
  }

  const handleFileUpload = async (file) => {
    if (!file) return

    setUploading(true)
    try {
      await uploadFile(departmentCode, file)
      await loadFiles()
      setSearchQuery('')
    } catch (error) {
      console.error('Error uploading file:', error)
      alert(error.response?.data?.detail || 'Failed to upload file. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      handleFileUpload(file)
      e.target.value = ''
    }
  }

  const handleDeleteFile = async (filename, e) => {
    e.stopPropagation()
    if (window.confirm(`Are you sure you want to delete "${filename.split('_').slice(1).join('_')}"?`)) {
      setDeleting(prev => ({ ...prev, [filename]: true }))
      try {
        await deleteFile(departmentCode, filename)
        await loadFiles()
      } catch (error) {
        console.error('Error deleting file:', error)
        alert('Failed to delete file.')
      } finally {
        setDeleting(prev => ({ ...prev, [filename]: false }))
      }
    }
  }

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

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0])
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const getFileTypeColor = (filename) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return 'var(--error-color)';
    if (['doc', 'docx'].includes(ext)) return 'var(--info-color)';
    if (ext === 'txt') return 'var(--text-secondary)';
    return 'var(--text-secondary)';
  }

  const handleThemeToggle = (e) => {
    e.preventDefault()
    e.stopPropagation()
    toggleTheme()
  }

  return (
    <div className="documents-page">
      {/* Header */}
      <div className="documents-header">
        <div className="header-left">
          <button
            className="back-btn"
            onClick={() => navigate(`/chat/${departmentCode}`)}
            title="Back to Chat"
          >
            <ArrowLeft size={20} />
          </button>
          <div className="department-info">
            <h1>{department?.name || (departmentCode ? departmentCode.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Department')}</h1>
            <span className="department-code">Documents & SOPs</span>
          </div>
        </div>

        <div className="header-right">
          <button
            className="theme-toggle-btn"
            onClick={handleThemeToggle}
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="documents-content">
        {/* Upload Section */}
        <div className="upload-section">
          <div
            ref={dropZoneRef}
            className={`drop-zone ${dragActive ? 'active' : ''} ${uploading ? 'uploading' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.docx,.txt,.doc"
              style={{ display: 'none' }}
            />
            
            {uploading ? (
              <div className="upload-status">
                <Loader className="upload-icon" size={48} />
                <h3>Uploading...</h3>
                <p>Please wait while your file is being processed</p>
              </div>
            ) : (
              <div className="upload-content">
                <div className="upload-icon-wrapper">
                  <Upload size={64} />
                </div>
                <h2>Upload Documents</h2>
                <p>Drag and drop files here, or click to browse</p>
                <div className="upload-info">
                  <span>Supported: PDF, DOCX, TXT, DOC</span>
                  <span>Max size: 50MB</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Search Section */}
        <div className="search-section">
          <div className="search-wrapper">
            <Search className="search-icon" size={20} />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            {searchQuery && (
              <button
                className="clear-search-btn"
                onClick={() => setSearchQuery('')}
                title="Clear search"
              >
                <X size={16} />
              </button>
            )}
          </div>
          <div className="files-count">
            {filteredFiles.length} {filteredFiles.length === 1 ? 'document' : 'documents'}
          </div>
        </div>

        {/* Files Grid */}
        <div className="files-section">
          {filteredFiles.length === 0 ? (
            <div className="empty-files">
              <FileText size={80} />
              <h2>{searchQuery ? 'No documents found' : 'No documents uploaded yet'}</h2>
              <p>{searchQuery ? 'Try a different search term' : 'Upload your first document to get started'}</p>
            </div>
          ) : (
            <div className="files-grid">
              {filteredFiles.map((file, index) => (
                <div
                  key={file.filename}
                  className="file-card"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div className="file-card-header">
                    <div className="file-icon-wrapper" style={{ color: getFileTypeColor(file.filename) }}>
                      <FileText size={32} />
                    </div>
                    <button
                      className="delete-file-btn"
                      onClick={(e) => handleDeleteFile(file.filename, e)}
                      disabled={deleting[file.filename]}
                      title="Delete file"
                    >
                      {deleting[file.filename] ? (
                        <Loader size={16} />
                      ) : (
                        <Trash2 size={16} />
                      )}
                    </button>
                  </div>
                  
                  <div className="file-card-content">
                    <h3 className="file-name" title={file.original_filename || file.filename}>
                      {file.original_filename || file.filename}
                    </h3>
                    <div className="file-meta">
                      <div className="file-meta-item">
                        <FileType size={14} />
                        <span>{formatFileSize(file.size)}</span>
                      </div>
                      <div className="file-meta-item">
                        <Clock size={14} />
                        <span>{(() => {
                          const fileDate = new Date(file.modified)
                          if (isToday(fileDate)) {
                            return formatDistanceToNow(fileDate, { addSuffix: true })
                          } else if (isYesterday(fileDate)) {
                            return `Yesterday ${format(fileDate, 'HH:mm')}`
                          } else if (isThisWeek(fileDate)) {
                            return format(fileDate, 'EEEE HH:mm')
                          } else {
                            return format(fileDate, 'MMM dd, yyyy')
                          }
                        })()}</span>
                      </div>
                    </div>
                  </div>

                  <div className="file-card-footer">
                    <div className="file-status">
                      <CheckCircle size={14} />
                      <span>Uploaded</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DocumentsPage

