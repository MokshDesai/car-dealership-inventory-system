# Car Dealership Inventory System

A high-fidelity, production-ready **Car Dealership Inventory System** built using **Django REST Framework (DRF)** on the backend and **React (Vite)** on the frontend. The application features a custom, modern minimalist layout, role-based operations, real-time client-side pagination, search/filtering, and custom alert pop-up modals for action confirmations.

---

## 🎨 Design & Theme Principles
- **Editorial Minimalism**: Completely transparent, cardless columns separated by elegant thin horizontal rules and dividers, matching the design of premium SaaS platforms.
- **Warm Theme Aesthetics**: Built on a soft peach-cream canvas background (`#fff6f0`) with dark slate typography (`#1e1e1e`) and vibrant coral-orange accents (`#ff7253`).
- **Interactive Focus**: Custom underlines on active headers and form text inputs that transition to coral-orange upon user focus.
- **Balanced Sidebars**: Avoids blank spaces by rendering guides and policy outlines inside layout sidebars depending on the user's role.

---

## 🚀 Key Features

### 1. Secure Authentication & Authorization
- **Token-Based Sessions**: Registration and Login are validated against the Django database, saving credentials using local storage.
- **Role-Based Controls**:
  - **Admin**: Has permissions to add, edit details, delete, and restock fleet vehicles.
  - **Customer**: Authorized to browse, filter, and purchase vehicles (decrements inventory counts by 1).

### 2. Dashboard Interface (3-Column Desktop Grid)
- **Left Column**: Live fleet search form (search by Make, Model, Category, Min Price, Max Price) + **Operator Quick Guide**.
- **Center Column**: Main fleet list showing vehicle category badges, price tags, stock indicator states, and actions.
- **Right Column**:
  - *Admin View*: **Add Inventory** form + listing guidelines checklist.
  - *Customer View*: **Purchase Policies** guidelines (filling empty spaces cleanly).

### 3. Sliced Pagination
- Limits catalog listings to render exactly **4 vehicles per page**.
- Generates interactive **Previous** and **Next** button controls with page counts, automatically resetting page index to `1` when filters change.

### 4. Interactive Confirmation Pop-ups
- Discards standard inline messages. All actions (Login, Register, Add, Edit, Delete, Purchase, and Restock) generate modal popups showing operation status:
  - **Success Modal**: Shows a green checkmark circle with detailed success confirmation descriptions.
  - **Error Modal**: Shows a red warning circle with specific API error descriptions.

---

## 🛠️ Technology Stack

- **Frontend**:
  - React 18
  - Vite (HMR and development bundler proxying API calls to port `8000`)
  - Vanilla CSS Variables (flexible global theme mappings)
- **Backend**:
  - Django 5.x
  - Django REST Framework (Token Authentication, API Views, Serializers)
  - SQLite (default relational database)
  - Django CORS Headers

---

## 📦 Project Directory Structure

```text
car-dealership-inventory-system/
├── backend/
│   ├── car_dealership_inventory/
│   │   ├── app/                    # Django Application logic (Models, Views, Serializers)
│   │   └── car_dealership_inventory/# Project configurations (settings, routing)
│   └── manage.py
├── frontend/
│   └── frontend/
│       ├── src/
│       │   ├── App.jsx             # Main App layout & API handlers
│       │   ├── App.css             # Main stylesheet (layout, theme vars, animations)
│       │   ├── api.js              # Fetch requests pointing to backend /api
│       │   └── main.jsx
│       ├── index.html
│       ├── vite.config.js          # Handles /api proxies
│       └── package.json
└── venv/                           # Python Virtual Environment
```

---

## ⚙️ Local Installation & Setup

### Prerequisites
Make sure you have the following installed on your machine:
- **Python 3.10+**
- **Node.js 18+**

---

### Backend Setup (Django)

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Activate the Virtual Environment**:
   - On macOS/Linux:
     ```bash
     source ../venv/bin/activate
     ```
   - On Windows:
     ```bash
     ..\venv\Scripts\activate
     ```

3. **Install Dependencies**:
   Ensure `django`, `djangorestframework`, and `django-cors-headers` are installed:
   ```bash
   pip install django djangorestframework django-cors-headers
   ```

4. **Run Database Migrations**:
   Create and update database schema definitions:
   ```bash
   python manage.py migrate
   ```

5. **Create an Admin Superuser**:
   Create a login for database control and system overrides:
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the Django Development Server**:
   Launch the backend server locally on port `8000`:
   ```bash
   python manage.py runserver
   ```
   *The API endpoints will be accessible at `http://localhost:8000/api/`.*

---

### Frontend Setup (Vite + React)

1. **Open a new terminal session and navigate to the frontend directory**:
   ```bash
   cd frontend/frontend
   ```

2. **Install Node Packages**:
   ```bash
   npm install
   ```

3. **Start the Vite Development Server**:
   ```bash
   npm run dev
   ```
   *The frontend application will boot locally on `http://localhost:5173`.*

4. **Compile Production Bundle (Optional)**:
   To verify build compiling:
   ```bash
   npm run build
   ```

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/login/` | Log in user and fetch token | No |
| **POST** | `/api/register/` | Register new customer or admin | No |
| **GET** | `/api/vehicles/` | Retrieve and filter fleet vehicles | Yes |
| **POST** | `/api/vehicles/` | Add new vehicle metadata | Yes (Admin) |
| **PUT** | `/api/vehicles/<id>/` | Update specific vehicle parameters | Yes (Admin) |
| **DELETE**| `/api/vehicles/<id>/` | Delete vehicle listing from database | Yes (Admin) |
| **POST** | `/api/vehicles/<id>/purchase/`| Decrement quantity stock count by 1 | Yes (Customer) |
| **POST** | `/api/vehicles/<id>/restock/` | Add units to quantity stock count | Yes (Admin) |

---