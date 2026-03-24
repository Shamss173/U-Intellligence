import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Send, Upload, MessageSquare, Trash2, Clock, X, Menu, Brain, BrainCircuit, Moon, Sun, Save, Sparkles, Zap, Search, FileText, ChevronLeft, ChevronRight } from 'lucide-react'
import { sendMessage, getConversations, getConversationDetail, deleteConversation, toggleMemory, uploadFile, getDepartment } from '../services/api'
import { formatDistanceToNow, format, isToday, isYesterday, isThisWeek, isThisMonth } from 'date-fns'
import { useTheme } from '../contexts/ThemeContext'
import './ChatInterface.css'

const ChatInterface = () => {
  const { departmentCode } = useParams()
  const navigate = useNavigate()
  const { theme, toggleTheme } = useTheme()
  const [department, setDepartment] = useState(null)
  const [conversations, setConversations] = useState([])
  const [currentConversation, setCurrentConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [memoryEnabled, setMemoryEnabled] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [memoryToggling, setMemoryToggling] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [generatingResponse, setGeneratingResponse] = useState(false)
  const [thinking, setThinking] = useState(false)
  const [filteredConversations, setFilteredConversations] = useState([])
  const messagesEndRef = useRef(null)
  const thinkingTimeoutRef = useRef(null)
  const fileInputRef = useRef(null)
  const sidebarRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    loadDepartment()
    loadConversations()
    if (inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [departmentCode])

  useEffect(() => {
    if (currentConversation) {
      loadConversationMessages(currentConversation.id)
      setMemoryEnabled(currentConversation.memory_enabled)
    } else {
      setMessages([])
    }
  }, [currentConversation])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Filter conversations based on search
    if (searchQuery.trim() === '') {
      setFilteredConversations(conversations)
    } else {
      const filtered = conversations.filter(conv =>
        conv.title?.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setFilteredConversations(filtered)
    }
  }, [searchQuery, conversations])


  useEffect(() => {
    const handleKeyPress = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setSidebarOpen(prev => !prev)
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [sidebarOpen])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

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

  const loadConversations = async () => {
    try {
      const data = await getConversations(departmentCode)
      setConversations(data)
      setFilteredConversations(data)
    } catch (error) {
      console.error('Error loading conversations:', error)
    }
  }

  const loadConversationMessages = async (conversationId) => {
    try {
      const data = await getConversationDetail(conversationId)
      setMessages(data.messages || [])
      setMemoryEnabled(data.memory_enabled)
    } catch (error) {
      console.error('Error loading messages:', error)
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return

    const messageText = inputMessage.trim()
    setInputMessage('')
    setLoading(true)
    setSaving(true)
    setThinking(true)

    // Add user message immediately
    setMessages(prev => [
      ...prev,
      { role: 'user', content: messageText, timestamp: new Date().toISOString() }
    ])

    // Transition to generating response after a brief thinking period
    thinkingTimeoutRef.current = setTimeout(() => {
      setThinking(false)
      setGeneratingResponse(true)
    }, 1500)

    try {
      const response = await sendMessage(
        departmentCode,
        messageText,
        currentConversation?.id || null,
        memoryEnabled
      )

      if (response.conversation_id) {
        if (!currentConversation || currentConversation.id !== response.conversation_id) {
          await loadConversations()
          const allConvs = await getConversations(departmentCode)
          const conv = allConvs.find(c => c.id === response.conversation_id)
          if (conv) {
            setCurrentConversation(conv)
            setMemoryEnabled(conv.memory_enabled)
          }
        } else {
          const updatedConv = await getConversationDetail(response.conversation_id)
          setMemoryEnabled(updatedConv.memory_enabled)
        }
      }

      // Clear thinking timeout since we got response
      if (thinkingTimeoutRef.current) {
        clearTimeout(thinkingTimeoutRef.current)
        thinkingTimeoutRef.current = null
      }

      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: response.message, timestamp: response.timestamp || new Date().toISOString() }
      ])

      await loadConversations()
    } catch (error) {
      console.error('Error sending message:', error)
      // Clear thinking timeout since we got an error
      if (thinkingTimeoutRef.current) {
        clearTimeout(thinkingTimeoutRef.current)
        thinkingTimeoutRef.current = null
      }
      // Remove the user message and add error message
      setMessages(prev => [
        ...prev.slice(0, -1), // Remove the user message
        { role: 'assistant', content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message || 'Unknown error'}. Please try again.`, timestamp: new Date().toISOString() }
      ])
      alert(`Failed to send message: ${error.response?.data?.detail || error.message || 'Unknown error'}. Please try again.`)
    } finally {
      setLoading(false)
      setSaving(false)
      setThinking(false)
      setGeneratingResponse(false)
      // Clear timeout in case it's still running
      if (thinkingTimeoutRef.current) {
        clearTimeout(thinkingTimeoutRef.current)
        thinkingTimeoutRef.current = null
      }
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }

  const handleNewConversation = () => {
    setCurrentConversation(null)
    setMessages([])
    setInputMessage('')
    setTimeout(() => inputRef.current?.focus(), 100)
  }

  const handleSelectConversation = async (conversation) => {
    setCurrentConversation(conversation)
  }

  const handleDeleteConversation = async (conversationId, e) => {
    e.stopPropagation()
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      try {
        await deleteConversation(conversationId)
        if (currentConversation?.id === conversationId) {
          setCurrentConversation(null)
          setMessages([])
        }
        await loadConversations()
      } catch (error) {
        console.error('Error deleting conversation:', error)
        alert('Failed to delete conversation.')
      }
    }
  }

  const handleToggleMemory = async () => {
    setMemoryToggling(true)
    const newMemoryState = !memoryEnabled

    if (currentConversation) {
      try {
        await toggleMemory(currentConversation.id, newMemoryState)
        setMemoryEnabled(newMemoryState)
        await loadConversationMessages(currentConversation.id)
      } catch (error) {
        console.error('Error toggling memory:', error)
        alert('Failed to toggle memory.')
        setMemoryToggling(false)
        return
      }
    } else {
      setMemoryEnabled(newMemoryState)
    }
    
    setMemoryToggling(false)
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    try {
      await uploadFile(departmentCode, file)
      alert('File uploaded successfully!')
      fileInputRef.current.value = ''
    } catch (error) {
      console.error('Error uploading file:', error)
      alert('Failed to upload file. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleThemeToggle = (e) => {
    e.preventDefault()
    e.stopPropagation()
    toggleTheme()
  }

  const formatConversationTime = (timestamp) => {
    const date = new Date(timestamp + (timestamp.includes('Z') ? '' : 'Z'))

    if (isToday(date)) {
      return `Today ${format(date, 'HH:mm')}`
    } else if (isYesterday(date)) {
      return `Yesterday ${format(date, 'HH:mm')}`
    } else if (isThisWeek(date)) {
      return format(date, 'EEEE HH:mm')
    } else if (isThisMonth(date)) {
      return format(date, 'MMM dd, HH:mm')
    } else {
      return format(date, 'MMM dd, yyyy HH:mm')
    }
  }

  const toggleSidebar = () => {
    setSidebarOpen(prev => !prev)
  }

  return (
    <div className="chat-interface">
      {/* Enhanced Sidebar with Slide Animation */}
      <div 
        ref={sidebarRef}
        className={`chat-sidebar ${sidebarOpen ? 'open' : 'closed'}`}
      >
        <div className="sidebar-header">
          <div className="sidebar-header-content">
            <MessageSquare className="sidebar-icon" size={24} />
            <h2>Conversations</h2>
            <span className="conversation-count">{conversations.length}</span>
          </div>
          <button
            className="new-conversation-btn"
            onClick={handleNewConversation}
            title="New Conversation"
          >
            <MessageSquare size={18} />
            <span>New</span>
          </button>
        </div>

        {/* Search Conversations */}
        <div className="sidebar-search">
          <Search className="search-icon" size={18} />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="sidebar-search-input"
          />
          {searchQuery && (
            <button
              className="clear-search-btn"
              onClick={() => setSearchQuery('')}
              title="Clear search"
            >
              <X size={14} />
            </button>
          )}
        </div>

        <div className="conversations-list">
          {filteredConversations.length === 0 ? (
            <div className="no-conversations">
              <MessageSquare size={48} />
              <p>{searchQuery ? 'No conversations found' : 'No conversations yet'}</p>
              <span>{searchQuery ? 'Try a different search' : 'Start a new conversation to begin!'}</span>
            </div>
          ) : (
            filteredConversations.map((conv, index) => (
              <div
                key={conv.id}
                className={`conversation-item ${currentConversation?.id === conv.id ? 'active' : ''}`}
                onClick={() => handleSelectConversation(conv)}
                style={{ animationDelay: `${index * 0.03}s` }}
              >
                <div className="conversation-content">
                  <div className="conversation-header">
                    <h4 className="conversation-title">{conv.title || 'Untitled'}</h4>
                    {saving && currentConversation?.id === conv.id && (
                      <Save className="saving-icon" size={14} />
                    )}
                    {conv.memory_enabled && (
                      <Brain className="memory-badge" size={12} title="Memory Enabled" />
                    )}
                  </div>
                  <div className="conversation-meta">
                    <Clock size={12} />
                    <span>{formatConversationTime(conv.created_at)}</span>
                    <span className="message-count">{conv.message_count} msgs</span>
                  </div>
                </div>
                <button
                  className="delete-conversation-btn"
                  onClick={(e) => handleDeleteConversation(conv.id, e)}
                  title="Delete Conversation"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Sidebar Toggle Button - Always Visible, Slides with Sidebar */}
      <button
        className={`sidebar-toggle-button ${sidebarOpen ? 'open' : 'closed'}`}
        onClick={toggleSidebar}
        title={sidebarOpen ? 'Hide Sidebar' : 'Show Sidebar'}
        style={{
          left: sidebarOpen ? '380px' : '0'
        }}
      >
        {sidebarOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
      </button>


      {/* Main Chat Area - Auto Adjusts Based on Sidebar State */}
      <div className={`chat-main ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        {/* Enhanced Header */}
        <div className="chat-header">
          <div className="header-left">
            <button
              className="back-btn"
              onClick={() => navigate('/')}
              title="Back to Departments"
            >
              <ArrowLeft size={20} />
            </button>
            <div className="department-info">
              <h1>{department?.name || (departmentCode ? departmentCode.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Department')}</h1>
              <span className="department-code">{departmentCode}</span>
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

            <button
              className="documents-btn"
              onClick={() => navigate(`/documents/${departmentCode}`)}
              title="View Documents"
            >
              <FileText size={18} />
              <span>Documents</span>
            </button>

            <label className="upload-btn">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept=".pdf,.docx,.txt,.doc"
                style={{ display: 'none' }}
              />
              <Upload size={18} />
              <span>{uploading ? 'Uploading...' : 'Upload'}</span>
            </label>

            {/* Enhanced Memory Toggle */}
            <div className="memory-toggle-container">
              <button
                className={`memory-toggle-btn ${memoryEnabled ? 'enabled' : 'disabled'} ${memoryToggling ? 'toggling' : ''}`}
                onClick={handleToggleMemory}
                disabled={memoryToggling}
                title={memoryEnabled ? 'Memory Enabled - Click to disable' : 'Memory Disabled - Click to enable'}
              >
                <div className="memory-toggle-inner">
                  {memoryEnabled ? (
                    <BrainCircuit className="memory-icon" size={20} />
                  ) : (
                    <Brain className="memory-icon" size={20} />
                  )}
                  <span className="memory-label">Memory</span>
                  <div className={`memory-indicator ${memoryEnabled ? 'on' : 'off'}`}>
                    <div className="memory-indicator-dot"></div>
                  </div>
                </div>
                {memoryToggling && (
                  <div className="memory-toggle-loader">
                    <Sparkles size={12} />
                  </div>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">
                <MessageSquare size={80} />
              </div>
              <h2>Start a conversation</h2>
              <p>Ask questions about {department?.name || (departmentCode ? departmentCode.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'your department')} SOPs and policies</p>
              <div className="empty-state-features">
                <div className="feature-item">
                  <Zap size={20} />
                  <span>Fast responses</span>
                </div>
                <div className="feature-item">
                  <Brain size={20} />
                  <span>Context-aware</span>
                </div>
                <div className="feature-item">
                  <Sparkles size={20} />
                  <span>AI-powered</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="messages-list">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`message ${msg.role === 'user' ? 'user-message' : 'assistant-message'}`}
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div className="message-content">
                    <p>{msg.content}</p>
                    <span className="message-timestamp">
                      {(() => {
                        const msgDate = new Date(msg.timestamp + (msg.timestamp.includes('Z') ? '' : 'Z'))
                        const now = new Date()

                        if (msgDate.toDateString() === now.toDateString()) {
                          // Today - just show time
                          return msgDate.toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit',
                            hour12: false
                          })
                        } else {
                          // Different day - show date and time
                          return msgDate.toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                            hour12: false
                          })
                        }
                      })()}
                    </span>
                  </div>
                </div>
              ))}
              {thinking && (
                <div className="message assistant-message thinking">
                  <div className="message-content">
                    <div className="thinking-indicator">
                      <div className="thinking-brain">
                        <span></span><span></span><span></span>
                      </div>
                    </div>
                    <div className="thinking-text">Analyzing your question...</div>
                  </div>
                </div>
              )}
              {generatingResponse && (
                <div className="message assistant-message generating">
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <div className="generating-text">Generating response...</div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Enhanced Input */}
        <div className="chat-input-container">
          <div className="chat-input-wrapper">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
              placeholder="Ask a question about SOPs and policies..."
              className="chat-input"
              disabled={loading}
            />
            <button
              className="send-btn"
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || loading}
              title="Send message"
            >
              {loading ? (
                <div className="send-btn-loader"></div>
              ) : (
                <Send size={20} />
              )}
            </button>
          </div>
          {saving && (
            <div className="saving-indicator">
              <Save size={14} />
              <span>Saving conversation...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
