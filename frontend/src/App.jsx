import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import DepartmentSelection from './components/DepartmentSelection'
import ChatInterface from './components/ChatInterface'
import DocumentsPage from './components/DocumentsPage'
import './App.css'

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="app">
          <Routes>
            <Route path="/" element={<DepartmentSelection />} />
            <Route path="/chat/:departmentCode" element={<ChatInterface />} />
            <Route path="/documents/:departmentCode" element={<DocumentsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  )
}

export default App

