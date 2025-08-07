# 💳 Credit Approval System

A Django-based backend system for managing and processing customer loan data. This project supports automated data ingestion from CSV files, customer and loan record APIs, and Docker-based deployment.

---

## 📁 Project Structure
```
credit_approval_system/
├── customer_data.csv                            # Initial customer data (CSV)
├── loan_data.csv                                # Initial loan data (CSV)
├── Dockerfile                                   # Docker image definition
├── docker-compose.yml                           # Docker Compose setup
├── entry_point.sh                               # Container entrypoint script
├── manage.py                                    # Django management script
├── requirements.txt                             # Python dependencies
│
├── credit_approval/                             # Main Django app
│ ├── admin.py
│ ├── apps.py
│ ├── models.py
│ ├── serializers.py
│ ├── urls.py
│ ├── views.py
│ ├── management/
│ │ └── commands/
│ │ └── ingest_data.py                           # Custom management command to ingest CSV data
│ └── migrations/
│ └── 0001_initial.py
│
└── credit_approval_system/                       # Django project configuration
├── settings.py
├── urls.py
├── wsgi.py
└── asgi.py
```


---

## 🚀 Features

- ✅ REST APIs for:
  - Registering customers
  - Creating loan applications
  - Checking loan eligibility
- 📂 Auto-ingestion of customer and loan data from CSV files at container startup
- 🐳 Full Docker & Docker Compose setup
- 🔄 Idempotent data ingestion via `update_or_create`

---

## ⚙️ Technologies Used

- Python 3.9
- Django & Django REST Framework
- PostgreSQL (via Docker)
- Docker & Docker Compose
- Pandas (for CSV handling)

---

## 🔧 Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/12Paradox34/alemenco_assigment.git
cd alemeco_assigment
```
### 2️⃣ Prepare CSV Files
Ensure these two files are present in the project root:

- customer_data.csv
- loan_data.csv
### 3️⃣ Run via Docker
```bash
docker-compose up --build
```
This will:

- Set up PostgreSQL
- Apply migrations
- Ingest customer and loan data
- Start the Django server at http://localhost:8000

## 🧠 Author
Ashish Kumar
📍 BIT Sindri | Aspiring SDE
📧 ak4970799@gmail.com



