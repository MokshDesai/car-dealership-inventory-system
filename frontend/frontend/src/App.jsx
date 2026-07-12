
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
  const [currentPage, setCurrentPage] = useState(1)
  const [confirmation, setConfirmation] = useState(null)

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
      setCurrentPage(1)
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
      setConfirmation({ success: true, message: 'Registration completed successfully! Welcome to the suite.' })
    } catch (error) {
      setConfirmation({ success: false, message: error.message })
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
      setConfirmation({ success: true, message: `Welcome back, ${form.username}! Access authorized.` })
    } catch (error) {
      setConfirmation({ success: false, message: error.message })
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
      const addedMakeModel = `${vehicleForm.make} ${vehicleForm.model}`
      setVehicleForm(emptyVehicle)
      setConfirmation({ success: true, message: `Vehicle "${addedMakeModel}" has been added to the fleet inventory.` })
      await loadVehicles()
    } catch (error) {
      setConfirmation({ success: false, message: error.message })
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
      const updatedMakeModel = `${vehicleForm.make} ${vehicleForm.model}`
      setEditId(null)
      setVehicleForm(emptyVehicle)
      setConfirmation({ success: true, message: `Vehicle "${updatedMakeModel}" details updated successfully.` })
      await loadVehicles()
    } catch (error) {
      setConfirmation({ success: false, message: error.message })
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this vehicle?')) return
    try {
      const targetVehicle = vehicles.find(v => v.id === id)
      const label = targetVehicle ? `${targetVehicle.make} ${targetVehicle.model}` : 'Vehicle'
      await deleteVehicle(id)
      setConfirmation({ success: true, message: `"${label}" was successfully removed from listings.` })
      await loadVehicles()
    } catch (error) {
      setConfirmation({ success: false, message: error.message })
    }
  }

  async function handlePurchase(id) {
    try {
      const targetVehicle = vehicles.find(v => v.id === id)
      const label = targetVehicle ? `${targetVehicle.make} ${targetVehicle.model}` : 'Vehicle'
      await purchaseVehicle(id)
      setConfirmation({ success: true, message: `Purchase transaction logged for "${label}".` })
      await loadVehicles()
    } catch (error) {
      setConfirmation({ success: false, message: error.message })
    }
  }

  async function handleRestock(id) {
    try {
      const targetVehicle = vehicles.find(v => v.id === id)
      const label = targetVehicle ? `${targetVehicle.make} ${targetVehicle.model}` : 'Vehicle'
      await restockVehicle(id)
      setConfirmation({ success: true, message: `"${label}" has been restocked.` })
      await loadVehicles()
    } catch (error) {
      setConfirmation({ success: false, message: error.message })
    }
  }

  // -------- LOGIN / REGISTER  --------
  if (!user) {
    const isSuccess = message && (message.toLowerCase().includes('success') || message.toLowerCase().includes('welcome'));
    return (
      <div className="auth-container">
        <header className="auth-header-clean">
          <h1 className="brand-logo-clean">
            Car <span className="brand-text-orange">Dealership</span>
          </h1>
          <p className="subtitle-clean">Inventory System</p>
        </header>

        <div className="auth-body">
          <div className="auth-left">
            <div className="auth-form-wrapper">
              {message && (
                <p className={`message ${isSuccess ? 'success' : 'error'}`}>
                  {message}
                </p>
              )}

              {page === 'login' ? (
                <form onSubmit={handleLogin}>
                  <h2>Welcome Back</h2>
                  <p className="form-desc">Please sign in to access your dashboard</p>
                  
                  <div className="input-group">
                    <label htmlFor="username">Username</label>
                    <input
                      id="username"
                      name="username"
                      placeholder="Enter your username"
                      value={form.username}
                      onChange={handleAuthChange}
                      required
                    />
                  </div>

                  <div className="input-group">
                    <label htmlFor="password">Password</label>
                    <input
                      id="password"
                      name="password"
                      type="password"
                      placeholder="Enter your password"
                      value={form.password}
                      onChange={handleAuthChange}
                      required
                    />
                  </div>

                  <button type="submit">Sign In</button>
                  
                  <p className="auth-switch">
                    New to the platform?{' '}
                    <button type="button" className="link-btn" onClick={() => setPage('register')}>
                      Create an account
                    </button>
                  </p>
                </form>
              ) : (
                <form onSubmit={handleRegister}>
                  <h2>Create Account</h2>
                  <p className="form-desc">Register to start managing inventory</p>

                  <div className="input-group">
                    <label htmlFor="reg-username">Username</label>
                    <input
                      id="reg-username"
                      name="username"
                      placeholder="Choose a username"
                      value={form.username}
                      onChange={handleAuthChange}
                      required
                    />
                  </div>

                  <div className="input-group">
                    <label htmlFor="reg-password">Password</label>
                    <input
                      id="reg-password"
                      name="password"
                      type="password"
                      placeholder="Choose a strong password"
                      value={form.password}
                      onChange={handleAuthChange}
                      required
                    />
                  </div>

                  <button type="submit">Register Now</button>

                  <p className="auth-switch">
                    Already have an account?{' '}
                    <button type="button" className="link-btn" onClick={() => setPage('login')}>
                      Sign in here
                    </button>
                  </p>
                </form>
              )}
            </div>
          </div>
          
          <div className="auth-right">
            <div className="auth-brand-content">
              <span className="brand-badge">DEALER SUITE</span>
              <h1 className="brand-headline">
                Manage inventory
                <br />
                at a glance.
              </h1>
              <p className="brand-tagline">
                Track vehicle pricing, restock quantities, and coordinate transactions in a pixel-perfect, unified console.
              </p>
              
              <h2 className="brand-sub-header">
                Built for sales professionals, inventory managers, and administrators who value speed.
              </h2>

              <div className="brand-points-list">
                <div className="brand-point-item">
                  <h3 className="brand-point-title primary-color">Accurate tracking</h3>
                  <p className="brand-point-sub">Live stock counts &bull; Category filtering &bull; Price metrics</p>
                </div>
                <div className="brand-point-item">
                  <h3 className="brand-point-title">Role-based controls</h3>
                  <p className="brand-point-sub">Restock actions &bull; Secure delete permissions &bull; Admin overrides</p>
                </div>
              </div>

              <div className="brand-footer-tags">
                <span>Fast</span>
                <span>Consistent</span>
                <span>Secure</span>
                <span>Structured</span>
              </div>
            </div>
          </div>
        </div>
      {confirmation && (
        <div className="modal-overlay" onClick={() => setConfirmation(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className={`modal-status-icon ${confirmation.success ? 'success' : 'error'}`}>
              {confirmation.success ? '✓' : '✗'}
            </div>
            <h2>{confirmation.success ? 'Success' : 'Notice'}</h2>
            <p>{confirmation.message}</p>
            <button 
              className={`modal-dismiss-btn ${confirmation.success ? 'success' : 'error'}`} 
              onClick={() => setConfirmation(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}
      </div>
    );
  }

  // -------- HOME / DASHBOARD  --------

  const PAGE_SIZE = 4;
  const indexOfLastVehicle = currentPage * PAGE_SIZE;
  const indexOfFirstVehicle = indexOfLastVehicle - PAGE_SIZE;
  const currentVehicles = vehicles.slice(indexOfFirstVehicle, indexOfLastVehicle);
  const totalPages = Math.ceil(vehicles.length / PAGE_SIZE);

  return (
    <div className="app">
      <header className="dashboard-header">
        <div className="logo-wrapper">
          <h1 className="brand-logo-clean">
            Car <span className="brand-text-orange">Dealership</span>
          </h1>
          <p className="subtitle-clean">Inventory System</p>
        </div>
        <div className="user-profile-capsule">
          <div className="user-avatar">{user.username[0].toUpperCase()}</div>
          <div className="user-info">
            <span className="username">{user.username}</span>
            <span className={`role-badge ${user.role}`}>{user.role}</span>
          </div>
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>
      </header>

      {message && <p className="message">{message}</p>}


      <div className="dashboard-layout">
        {/* Left Column: Search Filters */}
        <aside className="dashboard-sidebar-left">
          <section className="card form-card">
            <h2>🔍 Search Fleet</h2>
            <form className="search-form" onSubmit={handleSearch}>
              <div className="form-group">
                <label htmlFor="search-make">Make</label>
                <input id="search-make" name="make" placeholder="e.g. Toyota" value={filters.make} onChange={handleFilterChange} />
              </div>
              <div className="form-group">
                <label htmlFor="search-model">Model</label>
                <input id="search-model" name="model" placeholder="e.g. Camry" value={filters.model} onChange={handleFilterChange} />
              </div>
              <div className="form-group">
                <label htmlFor="search-category">Category</label>
                <input id="search-category" name="category" placeholder="e.g. Sedan" value={filters.category} onChange={handleFilterChange} />
              </div>
              <div className="form-group">
                <label htmlFor="search-min-price">Min Price ($)</label>
                <input id="search-min-price" name="min_price" placeholder="Min" value={filters.min_price} onChange={handleFilterChange} />
              </div>
              <div className="form-group">
                <label htmlFor="search-max-price">Max Price ($)</label>
                <input id="search-max-price" name="max_price" placeholder="Max" value={filters.max_price} onChange={handleFilterChange} />
              </div>
              <button type="submit" className="search-btn">Filter Fleet</button>
            </form>
          </section>

          <section className="card info-card">
            <h3>💡 Quick Guide</h3>
            <ul className="guide-list">
              <li>
                <strong>Role Rules:</strong> Admins manage records (Add/Edit/Delete/Restock). Customers execute sales (Purchase).
              </li>
              <li>
                <strong>Low Stock Warning:</strong> Status shifts to orange automatically when vehicle units drop to 5 or fewer.
              </li>
              <li>
                <strong>Valuation Model:</strong> Fleet valuation metrics and average valuations recalculate instantly.
              </li>
            </ul>
          </section>
        </aside>

        {/* Middle Column: Available Vehicles */}
        <main className="dashboard-main-content">
          <section className="card vehicles-list-card">
            <h2>🚗 Available Fleet Inventory {loading && '(loading...)'}</h2>
            <div className="vehicle-grid">
              {vehicles.length === 0 && <p className="no-vehicles">No vehicles found matching current search criteria.</p>}

              {currentVehicles.map((vehicle) => {
                const isLowStock = vehicle.quantity > 0 && vehicle.quantity <= 5;
                const isOutStock = vehicle.quantity === 0;
                return (
                  <div className="vehicle-card" key={vehicle.id}>
                    <div className="card-header">
                      <h3>{vehicle.make} {vehicle.model}</h3>
                      <span className="category-tag">{vehicle.category}</span>
                    </div>
                    
                    <div className="card-body">
                      <p className="price-row">
                        <strong>Valuation Price</strong>
                        <span className="price-tag">${Number(vehicle.price).toLocaleString()}</span>
                      </p>
                      <p className="stock-row">
                        <strong>Availability Status</strong>
                        <span className={`stock-badge ${isOutStock ? 'out' : isLowStock ? 'low' : 'ok'}`}>
                          {isOutStock ? 'Sold Out' : isLowStock ? `Low Stock (${vehicle.quantity})` : `In Stock (${vehicle.quantity})`}
                        </span>
                      </p>
                    </div>

                    <div className="actions">
                      <button
                        className="purchase-btn"
                        onClick={() => handlePurchase(vehicle.id)}
                        disabled={isOutStock}
                      >
                        {isOutStock ? 'Sold Out' : 'Purchase Vehicle'}
                      </button>

                      {isAdmin && (
                        <div className="admin-actions">
                          <button className="secondary" onClick={() => startEdit(vehicle)}>Edit</button>
                          <button className="secondary restock-btn" onClick={() => handleRestock(vehicle.id)}>Restock</button>
                          <button className="danger" onClick={() => handleDelete(vehicle.id)}>Delete</button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {totalPages > 1 && (
              <div className="pagination-controls">
                <button 
                  className="secondary prev-btn" 
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                >
                  &larr; Previous
                </button>
                <span className="page-indicator">
                  Page <strong>{currentPage}</strong> of {totalPages}
                </span>
                <button 
                  className="secondary next-btn" 
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                >
                  Next &rarr;
                </button>
              </div>
            )}
          </section>
        </main>

        {/* Right Column: Add/Update Form or Guidelines */}
        <aside className="dashboard-sidebar-right">
          {isAdmin ? (
            <>
              <section className="card form-card admin-card">
                <h2>🔧 {editId ? 'Edit Details' : 'Add Inventory'}</h2>
                <form className="vehicle-form" onSubmit={editId ? handleUpdateVehicle : handleAddVehicle}>
                  <div className="form-group">
                    <label htmlFor="form-make">Make</label>
                    <input id="form-make" name="make" placeholder="e.g. Honda" value={vehicleForm.make} onChange={handleVehicleFormChange} required />
                  </div>
                  <div className="form-group">
                    <label htmlFor="form-model">Model</label>
                    <input id="form-model" name="model" placeholder="e.g. Civic" value={vehicleForm.model} onChange={handleVehicleFormChange} required />
                  </div>
                  <div className="form-group">
                    <label htmlFor="form-category">Category</label>
                    <input id="form-category" name="category" placeholder="e.g. Hatchback" value={vehicleForm.category} onChange={handleVehicleFormChange} required />
                  </div>
                  <div className="form-group">
                    <label htmlFor="form-price">Price ($)</label>
                    <input id="form-price" name="price" placeholder="e.g. 25000" value={vehicleForm.price} onChange={handleVehicleFormChange} required />
                  </div>
                  <div className="form-group">
                    <label htmlFor="form-quantity">Quantity</label>
                    <input id="form-quantity" name="quantity" placeholder="Units in stock" value={vehicleForm.quantity} onChange={handleVehicleFormChange} required />
                  </div>
                  <div className="form-actions">
                    <button type="submit">{editId ? 'Update' : 'Add'}</button>
                    {editId && (
                      <button
                        type="button"
                        className="secondary cancel-btn"
                        onClick={() => {
                          setEditId(null);
                          setVehicleForm(emptyVehicle);
                        }}
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </form>
              </section>

              <section className="card info-card admin-guide-card">
                <h3>📋 Listing Guidelines</h3>
                <ul className="guide-list">
                  <li>Ensure prices are entered as positive integers in USD.</li>
                  <li>Categorize correctly (Sedan, SUV, Hatchback) to maintain index integrity.</li>
                  <li>Valuations recalculate dynamically across active models in real-time.</li>
                </ul>
              </section>
            </>
          ) : (
            <section className="card info-card client-info-card">
              <h2>📌 Purchase Policy</h2>
              <div className="guideline-content">
                <p className="guide-desc">
                  Welcome to the Dealership Operations Console. Browse active listings and process acquisitions.
                </p>
                <ul className="guide-list">
                  <li>
                    <strong>Acquisition:</strong> Purchase vehicle options decrement count instantly in real-time.
                  </li>
                  <li>
                    <strong>Out of Stock:</strong> Sold-out models require an administrator to restock.
                  </li>
                  <li>
                    <strong>Valuation:</strong> Pricing estimates are calculated dynamically based on listings.
                  </li>
                </ul>
              </div>
            </section>
          )}
        </aside>
      </div>
      {confirmation && (
        <div className="modal-overlay" onClick={() => setConfirmation(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className={`modal-status-icon ${confirmation.success ? 'success' : 'error'}`}>
              {confirmation.success ? '✓' : '✗'}
            </div>
            <h2>{confirmation.success ? 'Success' : 'Notice'}</h2>
            <p>{confirmation.message}</p>
            <button 
              className={`modal-dismiss-btn ${confirmation.success ? 'success' : 'error'}`} 
              onClick={() => setConfirmation(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
