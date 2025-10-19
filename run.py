"""
FlowDeck Application Entry Point
"""

from app import create_app, socketio, db
from app.database import init_database_features
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Flask application
app = create_app()


# Debug/diagnostic endpoints (safe to remove later)
@app.route('/__ping')
def __ping():
    return 'pong', 200


@app.route('/__routes')
def __routes():
    try:
        routes = sorted([f"{r.rule} -> {r.endpoint}" for r in app.url_map.iter_rules()])
        return "\n".join(routes), 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return f"error: {e}", 500   

@app.route('/__whoami')
def __whoami():
    try:
        from flask import current_app
        info = {
            'app_name': current_app.import_name,
            'id(app)': hex(id(current_app)),
            'url_map_count': len(list(current_app.url_map.iter_rules())),
        }
        return "\n".join(f"{k}: {v}" for k, v in info.items()), 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return f"error: {e}", 500

# Direct root test route to diagnose 404 issues (kept separate at /__root)
@app.route('/__root')
def __root():
    return 'root-ok', 200


@app.cli.command()
def init_db():
    """Initialize database with tables, triggers, views, and indexes"""
    with app.app_context():
        db.create_all()
        init_database_features(app)
        print("✅ Database initialized successfully!")


@app.cli.command()
def seed():
    """Seed database with initial data"""
    from app.utils.seed import seed_database
    with app.app_context():
        seed_database()


@app.cli.command()
def create_admin():
    """Create a new admin user"""
    from app.models import User, Role, Organisation
    import getpass
    
    with app.app_context():
        print("\n=== Create Admin User ===\n")
        
        # Get organisation
        orgs = Organisation.query.all()
        if not orgs:
            print("No organisations found. Please create an organisation first.")
            return
        
        print("Available organisations:")
        for i, org in enumerate(orgs, 1):
            print(f"{i}. {org.name} ({org.email})")
        
        org_choice = int(input("\nSelect organisation number: ")) - 1
        org = orgs[org_choice]
        
        # Get user details
        name = input("Admin name: ")
        email = input("Admin email: ")
        password = getpass.getpass("Password: ")
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            print(f"❌ User with email {email} already exists!")
            return
        
        # Create user
        user = User(
            name=name,
            email=email,
            organisation_id=org.id,
            is_active=True,
            is_email_verified=True
        )
        user.set_password(password)
        
        # Add admin role
        admin_role = Role.query.filter_by(name='Admin').first()
        if admin_role:
            user.roles.append(admin_role)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"\n✅ Admin user '{name}' created successfully!")


if __name__ == '__main__':
    # Run with Socket.IO
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"\n🚀 Starting FlowDeck on port {port}")
    print(f"📍 FLASK_PORT from .env: {os.getenv('FLASK_PORT')}")
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=False  # Disable reloader to see logs clearly
    )
