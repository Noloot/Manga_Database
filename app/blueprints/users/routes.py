from .schema import user_schema, users_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import User, db
from . import users_bp
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.util import encode_token, user_required, admin_required

@users_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        username = credentials["username"]
        password = credentials["password"]
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'error': e.messages}), 400
    
    query = select(User).where(User.username == username)
    user = db.session.execute(query).scalar_one_or_none()
    
    if user and check_password_hash(user.password, password):
        auth_token = encode_token(user.id, user.role)
        
        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@users_bp.route("/login/admin", methods=['POST'])
def admin_login():
    try:
        credentials = login_schema.load(request.json)
        username = credentials["username"]
        password = credentials["password"]
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'error': e.messages}), 400
    
    query = select(User).where(User.username == username)
    user = db.session.execute(query).scalar_one_or_none()
    
    if user and check_password_hash(user.password, password):
        if user.role != "admin":
            return jsonify({"message": "Access denied: Not an admin"}), 403
        
        auth_token = encode_token(user.id, user.role)
        return jsonify({
            "status": "success",
            "message": "Admin Logged in",
            "auth_token": auth_token
        }), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401
        
@users_bp.route("/", methods=['POST'])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    
    
    existing_user = db.session.execute(select(User).where((User.username == user_data.username) | (User.email == user_data.email))).scalar_one_or_none()
    
    if existing_user:
        return jsonify({
            "status": "fail",
            "message": "Username or email already exists"
            }), 409
    
    user_data.password = generate_password_hash(user_data.password)
    user_data.role = "user"
    
    try:
        db.session.add(user_data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Database error', 'error': str(e)}), 500
    
    return jsonify({'message': 'New user added successfully!', 'user': user_schema.dump(user_data)}), 201

@users_bp.route("/", methods=['GET'])
def get_users():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page
        total_count = db.session.query(User).count()
        
        query = select(User).offset(offset).limit(per_page)
        users = db.session.execute(query).scalars().all()
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_users': total_count,
            'users': users_schema.dump(users)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching Users', 'error': str(e)}), 500
    
@users_bp.route("/<int:id>", methods=['GET'])
def get_user(id):
    query = select(User).where(User.id == id)
    result = db.session.execute(query).scalars().first()
    
    if result is None:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify(user_schema.dump(result)), 200

@users_bp.route('/me', methods=['GET'])
@user_required
def get_my_profile():
    user = db.session.get(User, request.user_id)
    return jsonify(user_schema.dump(user)), 200

@users_bp.route('/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    try:
        user = user_schema.load(request.json, instance=user)
    except ValidationError as e:
        return jsonify({e.messages}), 400
    
    db.session.commit()
    return user_schema.jsonify(user), 200

@users_bp.route('/change-password', methods=['PUT'])
@user_required
def change_password():
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    user = db.session.get(User, request.user_id)
    
    if not check_password_hash(user.password, old_password):
        return jsonify({'message': 'Old password is incorrect'}), 400
    
    user.password = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200

@users_bp.route('/role/<int:id>', methods=['PUT'])
@admin_required
def change_user_role(id):
    data = request.json
    new_role = data.get('role')
    
    if new_role not in ['user', 'admin']:
        return jsonify({'message': 'Invalid role'}), 400
    
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.role = new_role
    db.session.commit()
    return jsonify({'message': f"User role updated to {new_role}"}), 200

@users_bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)
    
    if not user:
        return jsonify({'message': 'Invalid user id'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f"successfully deleted user {id}"}), 200