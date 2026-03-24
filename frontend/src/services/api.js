import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Departments API
export const getDepartments = async () => {
  const response = await api.get('/departments/')
  return response.data
}

export const getDepartment = async (code) => {
  const response = await api.get(`/departments/${code}`)
  return response.data
}

// Chat API
export const sendMessage = async (departmentId, message, conversationId = null, memoryEnabled = true) => {
  const response = await api.post('/chat/', {
    department_id: departmentId,
    message,
    conversation_id: conversationId,
    memory_enabled: memoryEnabled,
  })
  return response.data
}

export const getMessages = async (conversationId) => {
  const response = await api.get(`/chat/${conversationId}/messages`)
  return response.data
}

// Upload API
export const uploadFile = async (departmentId, file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post(`/upload/${departmentId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const listFiles = async (departmentId) => {
  const response = await api.get(`/upload/${departmentId}/files`)
  return response.data
}

export const deleteFile = async (departmentId, filename) => {
  const response = await api.delete(`/upload/${departmentId}/files/${encodeURIComponent(filename)}`)
  return response.data
}

// Conversations API
export const getConversations = async (departmentId) => {
  const response = await api.get(`/conversations/${departmentId}`)
  return response.data
}

export const getConversationDetail = async (conversationId) => {
  const response = await api.get(`/conversations/detail/${conversationId}`)
  return response.data
}

export const deleteConversation = async (conversationId) => {
  const response = await api.delete(`/conversations/${conversationId}`)
  return response.data
}

export const toggleMemory = async (conversationId, memoryEnabled) => {
  const response = await api.patch(`/conversations/${conversationId}/memory?memory_enabled=${memoryEnabled}`)
  return response.data
}

export default api
