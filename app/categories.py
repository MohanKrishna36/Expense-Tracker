from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from app.auth import login_required
from app.database import query_db, insert_db, update_db

bp = Blueprint('categories', __name__, url_prefix='/categories')

@bp.route('/')
@login_required
def index():
    """Show all categories."""
    # Get system categories (user_id is NULL) and user's custom categories
    categories = query_db(
        'SELECT * FROM categories WHERE user_id IS NULL OR user_id = ? ORDER BY name',
        (g.user['id'],)
    )
    return render_template('categories/index.html', categories=categories)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new category."""
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None

        if not name:
            error = 'Name is required.'
        
        if error is None:
            try:
                insert_db(
                    'INSERT INTO categories (name, description, user_id) VALUES (?, ?, ?)',
                    (name, description, g.user['id'])
                )
                flash(f'Category "{name}" was successfully created.', 'success')
                return redirect(url_for('categories.index'))
            except Exception as e:
                error = f"An error occurred: {e}"
        
        flash(error, 'error')
    
    return render_template('categories/create.html')

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    """Edit a category."""
    category = query_db(
        'SELECT * FROM categories WHERE id = ? AND user_id = ?',
        (id, g.user['id']),
        one=True
    )
    
    if category is None:
        flash('Category not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('categories.index'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None

        if not name:
            error = 'Name is required.'
        
        if error is None:
            try:
                update_db(
                    'UPDATE categories SET name = ?, description = ? WHERE id = ? AND user_id = ?',
                    (name, description, id, g.user['id'])
                )
                flash(f'Category "{name}" was successfully updated.', 'success')
                return redirect(url_for('categories.index'))
            except Exception as e:
                error = f"An error occurred: {e}"
        
        flash(error, 'error')
    
    return render_template('categories/edit.html', category=category)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Delete a category."""
    category = query_db(
        'SELECT * FROM categories WHERE id = ? AND user_id = ?',
        (id, g.user['id']),
        one=True
    )
    
    if category is None:
        flash('Category not found or you do not have permission to delete it.', 'error')
    else:
        # Check if the category is being used by any expenses
        expenses = query_db(
            'SELECT COUNT(*) as count FROM expenses WHERE category_id = ?',
            (id,),
            one=True
        )
        
        if expenses['count'] > 0:
            flash('Cannot delete category because it is being used by expenses.', 'error')
        else:
            try:
                update_db(
                    'DELETE FROM categories WHERE id = ? AND user_id = ?',
                    (id, g.user['id'])
                )
                flash('Category was successfully deleted.', 'success')
            except Exception as e:
                flash(f"An error occurred: {e}", 'error')
    
    return redirect(url_for('categories.index'))