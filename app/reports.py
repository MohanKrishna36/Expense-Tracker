from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from datetime import datetime, timedelta
import calendar
from app.auth import login_required
from app.database import query_db

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
@login_required
def index():
    """Show reports dashboard."""
    return render_template('reports/index.html')

@bp.route('/category')
@login_required
def category():
    """Show expenses by category."""
    # Get date range parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # If no dates provided, default to current month
    if not start_date or not end_date:
        today = datetime.now()
        start_date = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_date = datetime(today.year, today.month, last_day).strftime('%Y-%m-%d')
    
    # Get expenses grouped by category
    expenses_by_category = query_db(
        '''
        SELECT c.name as category_name, COALESCE(SUM(e.amount), 0) as total
        FROM categories c
        LEFT JOIN expenses e ON c.id = e.category_id AND e.user_id = ? 
                            AND e.date BETWEEN ? AND ?
        WHERE c.user_id IS NULL OR c.user_id = ?
        GROUP BY c.id
        ORDER BY total DESC
        ''',
        (g.user['id'], start_date, end_date, g.user['id'])
    )
    
    # Convert SQLite Row objects to dictionaries
    expenses_by_category = [dict(row) for row in expenses_by_category]
    
    # Calculate total expenses
    total_expenses = sum(item['total'] for item in expenses_by_category)
    
    # Add percentage to each category
    for item in expenses_by_category:
        if total_expenses > 0:
            item['percentage'] = round((item['total'] / total_expenses) * 100, 1)
        else:
            item['percentage'] = 0
    
    return render_template('reports/category.html', 
                          expenses=expenses_by_category,
                          total=total_expenses,
                          start_date=start_date,
                          end_date=end_date)

@bp.route('/monthly')
@login_required
def monthly():
    """Show monthly expense trends."""
    # Get year parameter, default to current year
    year = request.args.get('year', datetime.now().year)
    try:
        year = int(year)
    except ValueError:
        year = datetime.now().year
    
    # Get monthly totals for the selected year
    monthly_totals = query_db(
        '''
        SELECT strftime('%m', date) as month, 
               SUM(amount) as total
        FROM expenses
        WHERE user_id = ? AND strftime('%Y', date) = ?
        GROUP BY strftime('%m', date)
        ORDER BY month
        ''',
        (g.user['id'], str(year))
    )
    
    # Convert SQLite Row objects to dictionaries
    monthly_totals = [dict(row) for row in monthly_totals]
    
    # Create a list of all months with their totals
    months = []
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    for i in range(12):
        month_num = f"{i+1:02d}"
        month_data = next((item for item in monthly_totals if item['month'] == month_num), None)
        
        if month_data:
            months.append({
                'name': month_names[i],
                'number': month_num,
                'total': month_data['total']
            })
        else:
            months.append({
                'name': month_names[i],
                'number': month_num,
                'total': 0
            })
    
    # Get available years for the dropdown
    years = query_db(
        '''
        SELECT DISTINCT strftime('%Y', date) as year
        FROM expenses
        WHERE user_id = ?
        ORDER BY year DESC
        ''',
        (g.user['id'],)
    )
    
    years = [int(item['year']) for item in years]
    if not years and year not in years:
        years.append(year)
    
    return render_template('reports/monthly.html', 
                          months=months,
                          selected_year=year,
                          years=years)

@bp.route('/api/chart-data')
@login_required
def chart_data():
    """API endpoint to get chart data for the dashboard."""
    # Get current month's daily expenses
    today = datetime.now()
    current_month = today.month
    current_year = today.year
    start_date = datetime(current_year, current_month, 1).strftime('%Y-%m-%d')
    last_day = calendar.monthrange(current_year, current_month)[1]
    end_date = datetime(current_year, current_month, last_day).strftime('%Y-%m-%d')
    
    # Get category data for pie chart
    category_data = query_db(
        '''
        SELECT c.name as label, COALESCE(SUM(e.amount), 0) as value
        FROM categories c
        LEFT JOIN expenses e ON c.id = e.category_id AND e.user_id = ? 
                            AND e.date BETWEEN ? AND ?
        WHERE c.user_id IS NULL OR c.user_id = ?
        GROUP BY c.id
        HAVING value > 0
        ORDER BY value DESC
        ''',
        (g.user['id'], start_date, end_date, g.user['id'])
    )
    
    # Get daily data for line chart
    daily_data = query_db(
        '''
        SELECT date, SUM(amount) as total
        FROM expenses
        WHERE user_id = ? AND date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
        ''',
        (g.user['id'], start_date, end_date)
    )
    
    # Get monthly total data for the current year
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    monthly_total_data = query_db(
        '''
        SELECT strftime('%m', date) as month, SUM(amount) as total
        FROM expenses
        WHERE user_id = ? AND strftime('%Y', date) = ?
        GROUP BY strftime('%m', date)
        ORDER BY month
        ''',
        (g.user['id'], str(current_year))
    )
    
    # Format monthly data with month names
    monthly_total_formatted = []
    for row in monthly_total_data:
        month_num = int(row['month'])
        monthly_total_formatted.append({
            'month': row['month'],
            'month_name': month_names[month_num - 1],
            'total': row['total']
        })
    
    # Get budget comparison data (budget vs. spent) for the current month
    budget_comparison_data = query_db(
        '''
        SELECT c.name as category_name, 
               b.amount as budget_amount,
               COALESCE(SUM(e.amount), 0) as spent_amount
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        LEFT JOIN expenses e ON c.id = e.category_id 
                            AND e.user_id = ? 
                            AND strftime('%m', e.date) = ? 
                            AND strftime('%Y', e.date) = ?
        WHERE b.user_id = ? AND b.month = ? AND b.year = ?
        GROUP BY b.id
        ORDER BY c.name
        ''',
        (g.user['id'], f'{current_month:02d}', str(current_year), 
         g.user['id'], current_month, current_year)
    )
    
    # Convert SQLite Row objects to dictionaries
    category_data_dict = [dict(row) for row in category_data]
    daily_data_dict = [dict(row) for row in daily_data]
    budget_comparison_dict = [dict(row) for row in budget_comparison_data]
    
    # Format data for charts
    return jsonify({
        'categoryData': category_data_dict,
        'dailyData': daily_data_dict,
        'monthlyTotalData': monthly_total_formatted,
        'budgetComparisonData': budget_comparison_dict
    })