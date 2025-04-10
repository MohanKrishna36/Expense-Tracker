
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

## 🧪 Test Documentation

This section outlines the test flow to validate various functionalities of the Expense Tracker application.

### 1. User Authentication Testing

#### 1.1 Registration Testing
- Go to the registration page and enter:
  - Username: `testuser`
  - Email: `testuser@gmail.com`
  - Password: `testpassword123`
- Click **Register**
- Expect redirection to the login page with a success message

#### 1.2 Login Testing
- Enter:
  - Username: `testuser`
  - Password: `testpassword123`
- Click **Login**
- Expect redirection to the dashboard

---

### 2. Budget Management Testing

#### 2.1 Creating Budgets
- Navigate to **Budgets**
- Add a new budget for "Food" with ₹2000
- Check dashboard for:
  - Spent: ₹0
  - Remaining: ₹2000
  - Progress bar: 0%

#### 2.2 Adding Additional Budget
- Add another for "Entertainment" with ₹1000

---

### 3. Expense Management Testing

#### 3.1 Adding Expenses
- Navigate to **Expenses**
- Add an expense under "Food":
  - Amount: ₹500
  - Description: Grocery shopping
- Check updated "Food" budget:
  - Spent: ₹500
  - Remaining: ₹1500
  - Progress: 25% (Green)

#### 3.2 Add More Expenses
- Add ₹1300 under "Food" for Restaurant
- Total spent: ₹1800
- Progress: 90% (Yellow)

#### 3.3 Exceed Budget
- Add ₹300 for Coffee
- Total spent: ₹2100 on ₹2000 budget
- Progress: Over 100% (Red)

#### 3.4 Verify Budget Alert
- Check Alerts/Dashboard
- Verify red alert appears

---

### 4. Dashboard Testing

- Verify dashboard shows total budget, total spent, and % used
- Recent expenses list updated
- Budget alerts shown if applicable

---

### 5. Reports Testing

- Navigate to **Reports**
- View category-wise or monthly charts (Bar)
- Confirm data matches expenses

---

### 6. Editing & Deleting

#### 6.1 Edit Expense
- Change expense amount from ₹500 to ₹200
- Verify updates in dashboard and budget

#### 6.2 Edit Budget
- Increase budget from ₹2000 to ₹2500
- Alerts should update accordingly

#### 6.3 Delete Expense
- Remove expense and verify removal from all views

#### 6.4 Delete Budget
- Remove a budget; it should disappear from dashboard and alerts

---

### 7. Category Management

- Add new category (e.g., "Gifts")
- Use it in budgets/expenses
- Verify it's tracked properly

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