from flask import Flask
from flask_cors import CORS
import os
from .core.data_loader import DataLoader

# Global Data Loader Instance
loader = None

def create_app():
    global loader
    
    app = Flask(__name__, 
                static_folder='static', 
                template_folder='templates')
    
    # Secret key for sessions
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-dev-key')
    
    # Session configuration
    app.config['SESSION_COOKIE_SECURE'] = False  # Set True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # 7 days
    
    CORS(app, supports_credentials=True)
    
    # Initialize Data Loader
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    if loader is None:
        loader = DataLoader(BASE_DIR)
        loader.load_all_data()
    
    # Initialize Supabase Database
    try:
        from .core.database import init_database
        init_database()
    except Exception as e:
        print(f"[App] Database initialization warning: {e}")
    
    # Register Auth Blueprint
    from .auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    # Register Main Routes
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Register Diet Routes
    from .diet_routes import diet_bp
    app.register_blueprint(diet_bp)

    # Register Notification Routes
    from .notification_routes import notification_bp
    app.register_blueprint(notification_bp)
    
    # Initialize Notification System (Firebase + Scheduler)
    try:
        from .services.notification_service import init_notifications
        notification_status = init_notifications()
        print(f"[App] Notification system: Firebase={notification_status['firebase']}, Scheduler={notification_status['scheduler']}")
    except Exception as e:
        print(f"[App] Notification system initialization warning: {e}")

    return app

