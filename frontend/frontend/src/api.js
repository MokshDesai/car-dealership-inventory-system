// Simple helper to call Django API

const API = '/api'

function getToken() {
  return localStorage.getItem('token')
}

export function saveUser(user) {
  localStorage.setItem('token', user.token)
  localStorage.setItem('username', user.username)
  localStorage.setItem('role', user.role)
}

export function loadUser() {
  const token = getToken()
  if (!token) return null
  return {
    token,
    username: localStorage.getItem('username'),
    role: localStorage.getItem('role'),
  }
}

export function clearUser() {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
}

async function apiCall(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  const token = getToken()
  if (token) {
    headers.Authorization = `Token ${token}`
  }

  const response = await fetch(`${API}${url}`, {
    ...options,
    headers,
  })

  if (response.status === 204) {
    return null
  }

  const data = await response.json()

  if (!response.ok) {
    const message = data.error || data.detail || 'Something went wrong'
    throw new Error(message)
  }

  return data
}

export function register(username, email, password) {
  return apiCall('/auth/register/', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  })
}

export function login(username, password) {
  return apiCall('/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export function logout() {
  return apiCall('/auth/logout/', { method: 'POST' })
}

export function getVehicles(filters = {}) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.append(key, value)
  })
  const query = params.toString()
  return apiCall(`/vehicles/${query ? `?${query}` : ''}`)
}

export function addVehicle(vehicle) {
  return apiCall('/vehicles/', {
    method: 'POST',
    body: JSON.stringify(vehicle),
  })
}

export function updateVehicle(id, vehicle) {
  return apiCall(`/vehicles/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(vehicle),
  })
}

export function deleteVehicle(id) {
  return apiCall(`/vehicles/${id}/`, { method: 'DELETE' })
}

export function purchaseVehicle(id) {
  return apiCall(`/vehicles/${id}/purchase/`, { method: 'POST' })
}

export function restockVehicle(id) {
  return apiCall(`/vehicles/${id}/restock/`, { method: 'POST' })
}
