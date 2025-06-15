from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from jose.exceptions import JWTError, ExpiredSignatureError
from functools import wraps
from flask import request, jsonify
import os
import secrets

SECRET_KEY = os.environ.get('SECRET_KEY')

def encode_token(user_id, role):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(user_id),
        'role': role
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
                
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = int(data['sub'])
            request.role = data['role']
            
        except ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except JWTError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    @user_required
    def decorated(*args, **kwargs):
        if request.role != 'admin':
            return jsonify({'message': 'Unauthorized: Admin role required'}), 403
        return f(*args, **kwargs)
    
    return decorated
