import { useEffect, useState } from 'react'
import {
  addVehicle,
  clearUser,
  deleteVehicle,
  getVehicles,
  loadUser,
  login,
  logout,
  purchaseVehicle,
  register,
  restockVehicle,
  saveUser,
  updateVehicle,
} from './api'
import './App.css'

const emptyVehicle = {
  make: '',
  model: '',
  category: '',
  price: '',
  quantity: '',
}

function App() {
  const [page, setPage] = useState('login')
  const [user, setUser] = useState(loadUser())
  const [vehicles, setVehicles] = useState([])
  const [filters, setFilters] = useState({
    make: '',
    model: '',
    category: '',
    min_price: '',
    max_price: '',
  })
  const [form, setForm] = useState({ username: '', password: '' })
  const [vehicleForm, setVehicleForm] = useState(emptyVehicle)
  const [editId, setEditId] = useState(null)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const isAdmin = user?.role === 'admin'

  // Load vehicles when user is logged in
  useEffect(() => {
    if (user) {
      loadVehicles()
    }
  }, [user])

  async function loadVehicles() {
    try {
      setLoading(true)
      const data = await getVehicles(filters)
      setVehicles(data)
      setMessage('')
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  function handleAuthChange(event) {
    setForm({ ...form, [event.target.name]: event.target.value })
  }

  function handleFilterChange(event) {
    setFilters({ ...filters, [event.target.name]: event.target.value })
  }

  function handleVehicleFormChange(event) {
    setVehicleForm({ ...vehicleForm, [event.target.name]: event.target.value })
  }

  async function handleRegister(event) {
    event.preventDefault()
    try {
      const data = await register(form.username, form.password)
      saveUser(data)
      setUser({ token: data.token, username: data.username, role: data.role })
      setPage('home')
      setMessage('Registration successful!')
    } catch (error) {
      setMessage(error.message)
    }
  }

  async function handleLogin(event) {
    event.preventDefault()
    try {
      const data = await login(form.username, form.password)
      const userData = {
        token: data.token,
        username: form.username,
        role: data.role,
      }
      saveUser(userData)
      setUser(userData)
      setPage('home')
      setMessage('Welcome back!')
    } catch (error) {
      setMessage(error.message)
    }
  }

  async function handleLogout() {
    try {
      await logout()
    } catch (error) {
      // ignore logout errors
    }
    clearUser()
    setUser(null)
    setPage('login')
    setVehicles([])
    setMessage('')
  }

  async function handleSearch(event) {
    event.preventDefault()
    await loadVehicles()
  }

  async function handleAddVehicle(event) {
    event.preventDefault()
    try {
      await addVehicle({
        ...vehicleForm,
        price: vehicleForm.price,
        quantity: Number(vehicleForm.quantity),
      })
      setVehicleForm(emptyVehicle)
      setMessage('Vehicle added!')
      await loadVehicles()
    } catch (error) {
      setMessage(error.message)
    }
  }

  function startEdit(vehicle) {
    setEditId(vehicle.id)
    setVehicleForm({
      make: vehicle.make,
      model: vehicle.model,
      category: vehicle.category,
      price: String(vehicle.price),
      quantity: String(vehicle.quantity),
    })
  }

  async function handleUpdateVehicle(event) {
    event.preventDefault()
    try {
      await updateVehicle(editId, {
        ...vehicleForm,
        price: vehicleForm.price,
        quantity: Number(vehicleForm.quantity),
      })
      setEditId(null)
      setVehicleForm(emptyVehicle)
      setMessage('Vehicle updated!')
      await loadVehicles()
    } catch (error) {
      setMessage(error.message)
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this vehicle?')) return
    try {
      await deleteVehicle(id)
      setMessage('Vehicle deleted!')
      await loadVehicles()
    } catch (error) {
      setMessage(error.message)
    }
  }

  async function handlePurchase(id) {
    try {
      await purchaseVehicle(id)
      setMessage('Purchase successful!')
      await loadVehicles()
    } catch (error) {
      setMessage(error.message)
    }
  }

  async function handleRestock(id) {
    try {
      await restockVehicle(id)
      setMessage('Vehicle restocked!')
      await loadVehicles()
    } catch (error) {
      setMessage(error.message)
    }
  }

  // -------- LOGIN / REGISTER PAGES --------
  if (!user) {
    return (
      <div className="app">
        <div className="auth-box">
          <h1>Car Dealership</h1>
          <p className="subtitle">Inventory System</p>

          {message && <p className="message error">{message}</p>}

          {page === 'login' ? (
            <form onSubmit={handleLogin}>
              <h2>Login</h2>
              <input
                name="username"
                placeholder="Username"
                value={form.username}
                onChange={handleAuthChange}
                required
              />
              <input
                name="password"
                type="password"
                placeholder="Password"
                value={form.password}
                onChange={handleAuthChange}
                required
              />
              <button type="submit">Login</button>
              <p>
                New user?{' '}
                <button type="button" className="link-btn" onClick={() => setPage('register')}>
                  Register here
                </button>
              </p>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <h2>Register</h2>
              <input
                name="username"
                placeholder="Username"
                value={form.username}
                onChange={handleAuthChange}
                required
              />
              <input
                name="password"
                type="password"
                placeholder="Password"
                value={form.password}
                onChange={handleAuthChange}
                required
              />
              <button type="submit">Register</button>
              <p>
                Already have an account?{' '}
                <button type="button" className="link-btn" onClick={() => setPage('login')}>
                  Login here
                </button>
              </p>
            </form>
          )}
        </div>
      </div>
    )
  }

  // -------- HOME / DASHBOARD PAGE --------
  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Car Dealership</h1>
          <p>
            Hello, <strong>{user.username}</strong> ({user.role})
          </p>
        </div>
        <button onClick={handleLogout}>Logout</button>
      </header>

      {message && <p className="message">{message}</p>}

      <section className="card">
        <h2>Search Vehicles</h2>
        <form className="search-form" onSubmit={handleSearch}>
          <input name="make" placeholder="Make" value={filters.make} onChange={handleFilterChange} />
          <input name="model" placeholder="Model" value={filters.model} onChange={handleFilterChange} />
          <input name="category" placeholder="Category" value={filters.category} onChange={handleFilterChange} />
          <input name="min_price" placeholder="Min price" value={filters.min_price} onChange={handleFilterChange} />
          <input name="max_price" placeholder="Max price" value={filters.max_price} onChange={handleFilterChange} />
          <button type="submit">Search</button>
        </form>
      </section>

      {isAdmin && (
        <section className="card">
          <h2>{editId ? 'Update Vehicle' : 'Add New Vehicle'}</h2>
          <form className="vehicle-form" onSubmit={editId ? handleUpdateVehicle : handleAddVehicle}>
            <input name="make" placeholder="Make" value={vehicleForm.make} onChange={handleVehicleFormChange} required />
            <input name="model" placeholder="Model" value={vehicleForm.model} onChange={handleVehicleFormChange} required />
            <input name="category" placeholder="Category" value={vehicleForm.category} onChange={handleVehicleFormChange} required />
            <input name="price" placeholder="Price" value={vehicleForm.price} onChange={handleVehicleFormChange} required />
            <input name="quantity" placeholder="Quantity" value={vehicleForm.quantity} onChange={handleVehicleFormChange} required />
            <button type="submit">{editId ? 'Update' : 'Add Vehicle'}</button>
            {editId && (
              <button
                type="button"
                className="secondary"
                onClick={() => {
                  setEditId(null)
                  setVehicleForm(emptyVehicle)
                }}
              >
                Cancel
              </button>
            )}
          </form>
        </section>
      )}

      <section className="card">
        <h2>Available Vehicles {loading && '(loading...)'}</h2>
        <div className="vehicle-grid">
          {vehicles.length === 0 && <p>No vehicles found.</p>}

          {vehicles.map((vehicle) => (
            <div className="vehicle-card" key={vehicle.id}>
              <h3>{vehicle.make} {vehicle.model}</h3>
              <p><strong>Category:</strong> {vehicle.category}</p>
              <p><strong>Price:</strong> ${vehicle.price}</p>
              <p><strong>In stock:</strong> {vehicle.quantity}</p>

              <div className="actions">
                <button
                  onClick={() => handlePurchase(vehicle.id)}
                  disabled={vehicle.quantity === 0}
                >
                  {vehicle.quantity === 0 ? 'Out of Stock' : 'Purchase'}
                </button>

                {isAdmin && (
                  <>
                    <button className="secondary" onClick={() => startEdit(vehicle)}>Edit</button>
                    <button className="danger" onClick={() => handleDelete(vehicle.id)}>Delete</button>
                    <button className="secondary" onClick={() => handleRestock(vehicle.id)}>Restock</button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default App
