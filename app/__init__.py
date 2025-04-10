import os
from flask import Flask, render_template

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'expense_tracker.db'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register database functions
    from . import database
    database.init_app(app)

    # Register blueprints
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import categories
    app.register_blueprint(categories.bp)
    
    from . import expenses
    app.register_blueprint(expenses.bp)
    
    from . import budgets
    app.register_blueprint(budgets.bp)
    
    from . import reports
    app.register_blueprint(reports.bp)
    
    # Add this line where the other blueprints are registered
    from . import alerts
    app.register_blueprint(alerts.bp)

    # Home page route
    # Add this import with your other imports
    from . import dashboard
    
    # Register the dashboard blueprint and set it as the main route
    app.register_blueprint(dashboard.bp)
    app.add_url_rule('/', endpoint='index')
    def index():
        return render_template('index.html')

    return app