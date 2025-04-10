from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from datetime import datetime
from app.auth import login_required
from app.database import query_db, insert_db, update_db

bp = Blueprint('budgets', __name__, url_prefix='/budgets')

@bp.route('/')
@login_required
def index():
    """Show all budgets for the current month."""
    # Get current month and year
    current_date = datetime.now()
    month = current_date.month
    year = current_date.year
    
    # Get budgets for the current user and month
    budgets = query_db(
        '''
        SELECT b.*, c.name as category_name,
               (SELECT COALESCE(SUM(e.amount), 0)
                FROM expenses e
                WHERE e.category_id = b.category_id
                AND e.user_id = ?
                AND strftime('%m', e.date) = ?
                AND strftime('%Y', e.date) = ?) as spent
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ? AND b.month = ? AND b.year = ?
        ORDER BY c.name
        ''',
        (g.user['id'], f'{month:02d}', f'{year}', g.user['id'], month, year)
    )
    
    # Get categories that don't have a budget for this month
    categories_without_budget = query_db(
        '''
        SELECT c.*, 
               (SELECT COALESCE(SUM(e.amount), 0)
                FROM expenses e
                WHERE e.category_id = c.id
                AND e.user_id = ?
                AND strftime('%m', e.date) = ?
                AND strftime('%Y', e.date) = ?) as spent
        FROM categories c
        WHERE (c.user_id IS NULL OR c.user_id = ?)
        AND c.id NOT IN (
            SELECT category_id FROM budgets
            WHERE user_id = ? AND month = ? AND year = ?
        )
        ORDER BY c.name
        ''',
        (g.user['id'], f'{month:02d}', f'{year}', g.user['id'], g.user['id'], month, year)
    )
    
    return render_template('budgets/index.html', 
                          budgets=budgets, 
                          categories_without_budget=categories_without_budget,
                          current_month=current_date.strftime('%B %Y'))

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new budget."""
    # Get current month and year
    current_date = datetime.now()
    month = current_date.month
    year = current_date.year
    
    # Get categories that don't have a budget for this month
    categories = query_db(
        '''
        SELECT * FROM categories
        WHERE (user_id IS NULL OR user_id = ?)
        AND id NOT IN (
            SELECT category_id FROM budgets
            WHERE user_id = ? AND month = ? AND year = ?
        )
        ORDER BY name
        ''',
        (g.user['id'], g.user['id'], month, year)
    )
    
    if not categories:
        flash('All categories already have budgets for this month.', 'info')
        return redirect(url_for('budgets.index'))
    
    if request.method == 'POST':
        category_id = request.form['category_id']
        amount = request.form['amount']
        error = None

        if not category_id:
            error = 'Category is required.'
        elif not amount:
            error = 'Amount is required.'
        
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
                    'INSERT INTO budgets (amount, month, year, category_id, user_id) VALUES (?, ?, ?, ?, ?)',
                    (amount, month, year, category_id, g.user['id'])
                )
                flash('Budget was successfully added.', 'success')
                return redirect(url_for('budgets.index'))
            except Exception as e:
                error = f"An error occurred: {e}"
        
        flash(error, 'error')
    
    return render_template('budgets/create.html', 
                          categories=categories,
                          current_month=current_date.strftime('%B %Y'))

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    """Edit a budget."""
    budget = query_db(
        '''
        SELECT b.*, c.name as category_name
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.id = ? AND b.user_id = ?
        ''',
        (id, g.user['id']),
        one=True
    )
    
    if budget is None:
        flash('Budget not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('budgets.index'))
    
    if request.method == 'POST':
        amount = request.form['amount']
        error = None

        if not amount:
            error = 'Amount is required.'
        
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
                    'UPDATE budgets SET amount = ? WHERE id = ? AND user_id = ?',
                    (amount, id, g.user['id'])
                )
                flash('Budget was successfully updated.', 'success')
                return redirect(url_for('budgets.index'))
            except Exception as e:
                error = f"An error occurred: {e}"
        
        flash(error, 'error')
    
    return render_template('budgets/edit.html', budget=budget)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Delete a budget."""
    budget = query_db(
        'SELECT * FROM budgets WHERE id = ? AND user_id = ?',
        (id, g.user['id']),
        one=True
    )
    
    if budget is None:
        flash('Budget not found or you do not have permission to delete it.', 'error')
    else:
        try:
            update_db(
                'DELETE FROM budgets WHERE id = ? AND user_id = ?',
                (id, g.user['id'])
            )
            flash('Budget was successfully deleted.', 'success')
        except Exception as e:
            flash(f"An error occurred: {e}", 'error')
    
    return redirect(url_for('budgets.index'))