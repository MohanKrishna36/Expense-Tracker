import functools
from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app.auth import login_required
from app.database import get_db, query_db

bp = Blueprint('alerts', __name__, url_prefix='/alerts')

@bp.route('/')
@login_required
def index():
    """Show all active alerts for the current user."""
    # Get current month and year
    today = datetime.now()
    current_month = today.month
    current_year = today.year
    
    # Get budget alerts (where spending exceeds budget)
    budget_alerts = query_db(
        '''
        SELECT 
            c.name as category_name,
            b.id as budget_id,
            b.amount as budget_amount,
            COALESCE(SUM(e.amount), 0) as spent_amount,
            (COALESCE(SUM(e.amount), 0) - b.amount) as overspent_amount,
            ROUND((COALESCE(SUM(e.amount), 0) / b.amount) * 100, 1) as percentage
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        LEFT JOIN expenses e ON c.id = e.category_id 
                            AND e.user_id = ? 
                            AND strftime('%m', e.date) = ? 
                            AND strftime('%Y', e.date) = ?
        WHERE b.user_id = ? AND b.month = ? AND b.year = ?
        GROUP BY b.id
        HAVING spent_amount > budget_amount
        ORDER BY percentage DESC
        ''',
        (g.user['id'], f'{current_month:02d}', str(current_year), 
         g.user['id'], current_month, current_year)
    )
    
    # Get categories approaching budget (90% or more)
    approaching_alerts = query_db(
        '''
        SELECT 
            c.name as category_name,
            b.id as budget_id,
            b.amount as budget_amount,
            COALESCE(SUM(e.amount), 0) as spent_amount,
            (b.amount - COALESCE(SUM(e.amount), 0)) as remaining_amount,
            ROUND((COALESCE(SUM(e.amount), 0) / b.amount) * 100, 1) as percentage
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        LEFT JOIN expenses e ON c.id = e.category_id 
                            AND e.user_id = ? 
                            AND strftime('%m', e.date) = ? 
                            AND strftime('%Y', e.date) = ?
        WHERE b.user_id = ? AND b.month = ? AND b.year = ?
        GROUP BY b.id
        HAVING percentage >= 90 AND percentage < 100
        ORDER BY percentage DESC
        ''',
        (g.user['id'], f'{current_month:02d}', str(current_year), 
         g.user['id'], current_month, current_year)
    )
    
    # Convert SQLite Row objects to dictionaries
    budget_alerts = [dict(row) for row in budget_alerts]
    approaching_alerts = [dict(row) for row in approaching_alerts]
    
    # Get total number of alerts
    total_alerts = len(budget_alerts) + len(approaching_alerts)
    
    return render_template('alerts/index.html', 
                          budget_alerts=budget_alerts,
                          approaching_alerts=approaching_alerts,
                          total_alerts=total_alerts,
                          current_month=today.strftime('%B'),
                          current_year=current_year)