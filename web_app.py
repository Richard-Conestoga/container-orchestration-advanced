from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'userdb'),
    'user': os.getenv('DB_USER', 'appuser'),
    'password': os.getenv('DB_PASSWORD', 'changeme')
}

def get_db_connection():
    """Establish database connection with error handling"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

@app.route('/user', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'first_name' not in data or 'last_name' not in data:
            logger.warning(f"Invalid request data: {data}")
            return jsonify({'error': 'first_name and last_name are required'}), 400
        
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        
        if not first_name or not last_name:
            return jsonify({'error': 'first_name and last_name cannot be empty'}), 400
        
        # Insert user into database
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute(
            "INSERT INTO users (first_name, last_name) VALUES (%s, %s) RETURNING id, first_name, last_name, created_at",
            (first_name, last_name)
        )
        
        user = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"User created: ID={user['id']}, Name={first_name} {last_name}")
        
        return jsonify({
            'id': user['id'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'created_at': user['created_at'].isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Fetch a user by ID"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute(
            "SELECT id, first_name, last_name, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user is None:
            logger.info(f"User not found: ID={user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        logger.info(f"User fetched: ID={user_id}")
        
        return jsonify({
            'id': user['id'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'created_at': user['created_at'].isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/users', methods=['GET'])
def get_all_users():
    """Fetch all users (with pagination)"""
    try:
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute(
            "SELECT id, first_name, last_name, created_at FROM users ORDER BY id LIMIT %s OFFSET %s",
            (limit, offset)
        )
        
        users = cur.fetchall()
        cur.close()
        conn.close()
        
        logger.info(f"Fetched {len(users)} users")
        
        return jsonify({
            'users': [
                {
                    'id': u['id'],
                    'first_name': u['first_name'],
                    'last_name': u['last_name'],
                    'created_at': u['created_at'].isoformat()
                } for u in users
            ],
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)