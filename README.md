
```markdown
# 💰 Expense Tracker

A comprehensive web application for tracking personal expenses, managing budgets, and generating financial reports.

---

## 📌 Overview

Expense Tracker is a **Flask-based** web application designed to help users manage their personal finances. With this app, users can:

- Track daily expenses across various categories
- Set and monitor monthly budgets
- Receive alerts when nearing or exceeding budgets
- Generate reports to visualize spending patterns
- Manage custom expense categories

---

## ✨ Features

- 🔐 **User Authentication**: Secure login and registration
- 💸 **Expense Management**: Add, edit, and delete expenses
- 📊 **Budget Control**: Set budgets per category per month
- 🖥️ **Dashboard**: Overview of financial status
- 📈 **Reports**: Visualizations with charts
- 🔔 **Budget Alerts**: Notifications for budget limits
- 🗂️ **Category Management**: Custom expense categories

---

## ⚙️ Installation

### ✅ Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Flask

---

### 🔧 Standard Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MohanKrishna36/Expense-Tracker.git
   cd expense-tracker
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   # OR
   source venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   flask --app app init-db
   ```

5. **Run the application**
   ```bash
   flask --app app run
   ```

6. **Visit the app in your browser**
   ```
   http://localhost:5000
   ```

---

### 🐳 Docker Installation

1. Ensure **Docker Desktop** is installed and running.

2. **Build the Docker image**
   ```bash
   docker build -t expense-tracker .
   ```

3. **Run the container**
   ```bash
   docker run -p 5000:5000 expense-tracker
   ```

4. **Visit the app in your browser**
   ```
   http://localhost:5000
   ```

---

## 🧭 Usage Guide

### 👤 Registration and Login
1. Register a new account
2. Login with your credentials

### ➕ Adding Expenses
1. Go to **Expenses** from the menu
2. Click **Add Expense**
3. Fill in the amount, category, date, and description
4. Submit

### 📅 Creating Budgets
1. Navigate to **Budgets**
2. Click **Create Budget**
3. Select a category, month, and budget amount
4. Submit

### 📊 Viewing Reports
1. Go to **Reports**
2. View detailed monthly and category-wise spending trends

---

## 📁 Project Structure

```plaintext
expense-tracker/
├── app/                  
│   ├── __init__.py       
│   ├── auth.py           
│   ├── database.py       
│   ├── expenses.py       
│   ├── budgets.py        
│   ├── categories.py     
│   ├── reports.py        
│   ├── alerts.py         
│   ├── dashboard.py      
│   ├── schema.sql        
│   └── templates/        
├── instance/             
├── venv/                 
├── requirements.txt      
├── Dockerfile            
└── README.md             
```

---

## 🛠 Technologies Used

- **Backend**: Python, Flask  
- **Database**: SQLite  
- **Frontend**: HTML, CSS, JavaScript, Bootstrap  
- **Containerization**: Docker

---

## 📄 License

This project is licensed under the **MIT License**.

```

