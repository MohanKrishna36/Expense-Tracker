-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    category_id INTEGER,
    user_id INTEGER NOT NULL,
    shared BOOLEAN DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Budgets table
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories (id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(month, year, category_id, user_id)
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    threshold_percentage INTEGER NOT NULL,
    active BOOLEAN DEFAULT 1,
    user_id INTEGER NOT NULL,
    category_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (category_id) REFERENCES categories (id)
);

-- ExpenseShares table
CREATE TABLE IF NOT EXISTS expense_shares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    settled BOOLEAN DEFAULT 0,
    FOREIGN KEY (expense_id) REFERENCES expenses (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert default categories
INSERT OR IGNORE INTO categories (name, description, user_id) VALUES 
('Food', 'Groceries, restaurants, and other food expenses', NULL),
('Transport', 'Public transport, fuel, and other transportation costs', NULL),
('Entertainment', 'Movies, games, and other entertainment expenses', NULL),
('Utilities', 'Electricity, water, internet, and other utility bills', NULL),
('Housing', 'Rent, mortgage, and other housing expenses', NULL),
('Health', 'Medical expenses, insurance, and other health-related costs', NULL),
('Education', 'Tuition, books, and other education expenses', NULL),
('Shopping', 'Clothing, electronics, and other shopping expenses', NULL),
('Other', 'Miscellaneous expenses', NULL);