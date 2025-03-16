from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import json

# Import your existing models
from models import User, Base

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://esemicolonr.github.io"}})

# Database connection
def get_db_connection():
    # Get database connection info from environment variables or use defaults
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', 'postgres')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'loyalty_points')
    
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    return Session()

# Endpoint to get active user leaderboard
@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        session = get_db_connection()
        
        # Get stream activity threshold (default: last 30 minutes)
        minutes = request.args.get('minutes', 30, type=int)
        recent_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        # Get top 25 recently updated non-eliminated users by points
        top_users = session.query(User).filter(
            User.updated_at >= recent_time,
            User.is_eliminated == False
        ).order_by(desc(User.points)).limit(25).all()
        
        # Format the response
        leaderboard = [
            {
                'position': i+1,
                'username': user.username,
                'points': round(user.points, 1)  # Round to 1 decimal place
            }
            for i, user in enumerate(top_users)
        ]
        
        # Add stream status
        status = "active" if len(top_users) > 0 else "inactive"
        
        return jsonify({
            'status': status,
            'users': leaderboard,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if 'session' in locals():
            session.close()

# Simple status endpoint
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'status': 'online',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'API is working',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)