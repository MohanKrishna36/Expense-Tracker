from flask import (
    Blueprint, render_template, g
)
from datetime import datetime
from app.auth import login_required
from app.database import query_db

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def index():
    """Show dashboard with key financial information."""
    # Get current month and year
    today = datetime.now()
    current_month = today.month
    current_year = today.year
    
    # Get total expenses for current month
    current_month_expenses = query_db(
        '''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM expenses
        WHERE user_id = ? 
        AND strftime('%m', date) = ? 
        AND strftime('%Y', date) = ?
        ''',
        (g.user['id'], f'{current_month:02d}', str(current_year)),
        one=True
    )
    
    # Get total budget for current month
    current_month_budget = query_db(
        '''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM budgets
        WHERE user_id = ? AND month = ? AND year = ?
        ''',
        (g.user['id'], current_month, current_year),
        one=True
    )
    
    # Get recent expenses (last 5)
    recent_expenses = query_db(
        '''
        SELECT e.*, c.name as category_name 
        FROM expenses e 
        LEFT JOIN categories c ON e.category_id = c.id 
        WHERE e.user_id = ? 
        ORDER BY e.date DESC LIMIT 5
        ''',
        (g.user['id'],)
    )
    
    # Get budget alerts
    budget_alerts = query_db(
        '''
        SELECT 
            c.name as category_name,
            b.amount as budget_amount,
            COALESCE(SUM(e.amount), 0) as spent_amount,
            ROUND((COALESCE(SUM(e.amount), 0) / b.amount) * 100, 1) as percentage
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        LEFT JOIN expenses e ON c.id = e.category_id 
                            AND e.user_id = ? 
                            AND strftime('%m', e.date) = ? 
                            AND strftime('%Y', e.date) = ?
        WHERE b.user_id = ? AND b.month = ? AND b.year = ?
        GROUP BY b.id
        HAVING percentage >= 90
        ORDER BY percentage DESC
        LIMIT 3
        ''',
        (g.user['id'], f'{current_month:02d}', str(current_year), 
         g.user['id'], current_month, current_year)
    )
    
    return render_template('dashboard/index.html',
                          current_month=today.strftime('%B'),
                          current_year=current_year,
                          current_month_expenses=current_month_expenses['total'],
                          current_month_budget=current_month_budget['total'],
                          recent_expenses=recent_expenses,
                          budget_alerts=budget_alerts)