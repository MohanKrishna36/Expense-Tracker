from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from datetime import datetime
from app.auth import login_required
from app.database import query_db, insert_db, update_db

bp = Blueprint('expenses', __name__, url_prefix='/expenses')

def check_budget_alert(user_id, category_id, date):
    """Check if adding this expense triggers a budget alert."""
    # Extract month and year from date
    expense_date = datetime.strptime(date, '%Y-%m-%d')
    month = expense_date.month
    year = expense_date.year
    
    # Check if this expense pushes the category over budget
    budget_status = query_db(
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
        WHERE b.user_id = ? AND b.month = ? AND b.year = ? AND c.id = ?
        GROUP BY b.id
        ''',
        (user_id, f'{month:02d}', str(year), user_id, month, year, category_id),
        one=True
    )
    
    if budget_status:
        if budget_status['percentage'] >= 100:
            flash(f"Alert: You've exceeded your budget for {budget_status['category_name']}! (${budget_status['spent_amount']:.2f} of ${budget_status['budget_amount']:.2f})", 'danger')
        elif budget_status['percentage'] >= 90:
            flash(f"Warning: You've used {budget_status['percentage']}% of your budget for {budget_status['category_name']}! (${budget_status['spent_amount']:.2f} of ${budget_status['budget_amount']:.2f})", 'warning')

@bp.route('/')
@login_required
def index():
    """Show all expenses."""
    # Get expenses for the current user
    expenses = query_db(
        '''
        SELECT e.*, c.name as category_name 
        FROM expenses e 
        LEFT JOIN categories c ON e.category_id = c.id 
        WHERE e.user_id = ? 
        ORDER BY e.date DESC
        ''',
        (g.user['id'],)
    )
    return render_template('expenses/index.html', expenses=expenses)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new expense."""
    # Get categories for dropdown
    categories = query_db(
        'SELECT * FROM categories WHERE user_id IS NULL OR user_id = ? ORDER BY name',
        (g.user['id'],)
    )
    
    if request.method == 'POST':
        amount = request.form['amount']
        description = request.form['description']
        date = request.form['date']
        category_id = request.form['category_id']
        error = None

        if not amount:
            error = 'Amount is required.'
        elif not date:
            error = 'Date is required.'
        
        try:
            # Convert amount to float
            amount = float(amount)
            if amount <= 0:
                error = 'Amount must be greater than zero.'
        except ValueError:
            error = 'Amount must be a valid number.'
        
        if error is None:
            try:
                insert_db(
                    'INSERT INTO expenses (amount, description, date, category_id, user_id) VALUES (?, ?, ?, ?, ?)',
                    (amount, description, date, category_id, g.user['id'])
                )
                flash('Expense was successfully added.', 'success')
                
                # Check if this expense triggers a budget alert
                check_budget_alert(g.user['id'], category_id, date)
                
                return redirect(url_for('expenses.index'))
            except Exception as e:
                error = f"An error occurred: {e}"
        
        flash(error, 'error')
    
    # Get today's date for the date field
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('expenses/create.html', categories=categories, today=today)

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    """Edit an expense."""
    expense = query_db(
        'SELECT * FROM expenses WHERE id = ? AND user_id = ?',
        (id, g.user['id']),
        one=True
    )
    
    if expense is None:
        flash('Expense not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('expenses.index'))
    
    # Get categories for dropdown
    categories = query_db(
        'SELECT * FROM categories WHERE user_id IS NULL OR user_id = ? ORDER BY name',
        (g.user['id'],)
    )
    
    if request.method == 'POST':
        amount = request.form['amount']
        description = request.form['description']
        date = request.form['date']
        category_id = request.form['category_id']
        error = None

        if not amount:
            error = 'Amount is required.'
        elif not date:
            error = 'Date is required.'
        
        try:
            # Convert amount to float
            amount = float(amount)
            if amount <= 0:
                error = 'Amount must be greater than zero.'
        except ValueError:
            error = 'Amount must be a valid number.'
        
        if error is None:
            try:
                update_db(
                    'UPDATE expenses SET amount = ?, description = ?, date = ?, category_id = ? WHERE id = ? AND user_id = ?',
                    (amount, description, date, category_id, id, g.user['id'])
                )
                flash('Expense was successfully updated.', 'success')
                
                # Check if this expense update triggers a budget alert
                check_budget_alert(g.user['id'], category_id, date)
                
                return redirect(url_for('expenses.index'))
            except Exception as e:
                error = f"An error occurred: {e}"
        
        flash(error, 'error')
    
    return render_template('expenses/edit.html', expense=expense, categories=categories)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Delete an expense."""
    expense = query_db(
        'SELECT * FROM expenses WHERE id = ? AND user_id = ?',
        (id, g.user['id']),
        one=True
    )
    
    if expense is None:
        flash('Expense not found or you do not have permission to delete it.', 'error')
    else:
        try:
            update_db(
                'DELETE FROM expenses WHERE id = ? AND user_id = ?',
                (id, g.user['id'])
            )
            flash('Expense was successfully deleted.', 'success')
        except Exception as e:
            flash(f"An error occurred: {e}", 'error')
    
    return redirect(url_for('expenses.index'))