import functools
import hashlib
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app.database import get_db, query_db, insert_db
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.before_app_request
def load_logged_in_user():
    """Load user if user_id is stored in the session."""
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = query_db(
            'SELECT * FROM users WHERE id = ?', (user_id,), one=True
        )

@bp.before_app_request
def load_alerts_count():
    """Load the number of active alerts for the current user."""
    if g.user:
        # Get current month and year
        today = datetime.now()
        current_month = today.month
        current_year = today.year
        
        # Count budget alerts (where spending exceeds budget or reaches 90%)
        db = get_db()
        alerts_count = db.execute(
            '''
            SELECT COUNT(*) as count
            FROM (
                SELECT 
                    b.id,
                    COALESCE(SUM(e.amount), 0) as spent_amount,
                    b.amount as budget_amount
                FROM budgets b
                JOIN categories c ON b.category_id = c.id
                LEFT JOIN expenses e ON c.id = e.category_id 
                                    AND e.user_id = ? 
                                    AND strftime('%m', e.date) = ? 
                                    AND strftime('%Y', e.date) = ?
                WHERE b.user_id = ? AND b.month = ? AND b.year = ?
                GROUP BY b.id
                HAVING spent_amount > budget_amount * 0.9
            )
            ''',
            (g.user['id'], f'{current_month:02d}', str(current_year), 
             g.user['id'], current_month, current_year)
        ).fetchone()['count']
        
        g.alerts_count = alerts_count
    else:
        g.alerts_count = None

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif query_db('SELECT id FROM users WHERE username = ?', (username,), one=True) is not None:
            error = f"User {username} is already registered."
        elif query_db('SELECT id FROM users WHERE email = ?', (email,), one=True) is not None:
            error = f"Email {email} is already registered."
            
        if error is None:
            # Hash the password before storing
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            insert_db(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        
        flash(error, 'error')
    
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        
        user = query_db(
            'SELECT * FROM users WHERE username = ?', (username,), one=True
        )
        
        if user is None:
            error = 'Incorrect username.'
        else:
            # Hash the provided password and compare with stored hash
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] != password_hash:
                error = 'Incorrect password.'
        
        if error is None:
            # Store the user ID in a new session
            session.clear()
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        
        flash(error, 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    """Log out the current user."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))