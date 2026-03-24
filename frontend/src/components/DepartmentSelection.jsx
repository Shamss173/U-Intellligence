import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building2, ChevronDown, Search, Moon, Sun } from 'lucide-react'
import { getDepartments } from '../services/api'
import { useTheme } from '../contexts/ThemeContext'
import './DepartmentSelection.css'

const DepartmentSelection = () => {
  const [departments, setDepartments] = useState([])
  const [filteredDepartments, setFilteredDepartments] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [selectedDepartment, setSelectedDepartment] = useState(null)
  const dropdownRef = useRef(null)
  const navigate = useNavigate()
  const { theme, toggleTheme } = useTheme()

  useEffect(() => {
    loadDepartments()
  }, [])

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredDepartments(departments)
    } else {
      const filtered = departments.filter(dept =>
        dept.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        dept.description?.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setFilteredDepartments(filtered)
    }
  }, [searchQuery, departments])

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const loadDepartments = async () => {
    try {
      setLoading(true)
      const data = await getDepartments()
      setDepartments(data)
      setFilteredDepartments(data)
    } catch (error) {
      console.error('Error loading departments:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDepartmentSelect = (department) => {
    setSelectedDepartment(department)
    setDropdownOpen(false)
    navigate(`/chat/${department.code}`)
  }

  const handleThemeToggle = (e) => {
    e.preventDefault()
    e.stopPropagation()
    toggleTheme()
  }

  return (
    <div className="department-selection">
      {/* Theme Toggle */}
      <button 
        className="theme-toggle" 
        onClick={handleThemeToggle} 
        title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      >
        {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
      </button>

      <div className="department-selection-container">
        <div className="department-selection-header fade-in">
          <div className="logo-section">
            <div className="logo-wrapper">
              <Building2 className="logo-icon" size={56} />
            </div>
            <h1 className="main-title">U-Intelligence</h1>
          </div>
          <p className="subtitle">UBL Knowledge Assistant</p>
          <p className="description">
            Select your department to access department-specific SOPs, policies, and procedures
          </p>
        </div>

        {/* Enhanced Dropdown */}
        <div className="dropdown-section fade-in" ref={dropdownRef}>
          <div 
            className={`department-dropdown ${dropdownOpen ? 'open' : ''}`}
            onClick={() => setDropdownOpen(!dropdownOpen)}
          >
            <div className="dropdown-selected">
              <Building2 size={20} />
              <span className="dropdown-text">
                {selectedDepartment ? selectedDepartment.name : 'Select Department'}
              </span>
              <ChevronDown className={`dropdown-chevron ${dropdownOpen ? 'open' : ''}`} size={20} />
            </div>
          </div>

          {dropdownOpen && (
            <div className="dropdown-menu">
              <div className="dropdown-search">
                <Search className="search-icon" size={18} />
                <input
                  type="text"
                  placeholder="Search departments..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="dropdown-search-input"
                  onClick={(e) => e.stopPropagation()}
                />
              </div>
              <div className="dropdown-list">
                {loading ? (
                  <div className="dropdown-loading">
                    <div className="loading-spinner-small"></div>
                    <span>Loading departments...</span>
                  </div>
                ) : filteredDepartments.length > 0 ? (
                  filteredDepartments.map((dept, index) => (
                    <div
                      key={dept.id}
                      className="dropdown-item"
                      style={{ animationDelay: `${index * 0.02}s` }}
                      onClick={() => handleDepartmentSelect(dept)}
                    >
                      <div className="dropdown-item-content">
                        <h4 className="dropdown-item-name">{dept.name}</h4>
                        {dept.description && (
                          <p className="dropdown-item-desc">{dept.description}</p>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="dropdown-empty">
                    <p>No departments found</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DepartmentSelection
