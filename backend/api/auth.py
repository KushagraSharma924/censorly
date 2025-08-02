"""
Authentication routes for AI Profanity Filter SaaS Platform
JWT-based authentication with registration, login, and profile management.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)
from marshmallow import Schema, fields, ValidationError, validate
from models.saas_models import db, User
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def get_current_user_id():
    """Get current user ID from JWT, converted to integer."""
    try:
        user_id_str = get_jwt_identity()
        return int(user_id_str) if user_id_str else None
    except (ValueError, TypeError):
        return None


# Validation schemas
class UserRegistrationSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    full_name = fields.Str(validate=validate.Length(max=100))
    plan = fields.Str(validate=validate.OneOf(['free', 'pro', 'enterprise']), missing='free')


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class PasswordChangeSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))


def validate_password_strength(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    schema = UserRegistrationSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
    
    # Check password strength
    is_valid, message = validate_password_strength(data['password'])
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    try:
        # Create new user
        user = User(
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name'),
            plan=data.get('plan', 'free')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Create user directories
        user_upload_dir = current_app.config['Config'].get_user_upload_folder(user.id)
        user_processed_dir = current_app.config['Config'].get_user_processed_folder(user.id)
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        user_processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Create user-specific learned words file
        learned_words_path = current_app.config['Config'].get_user_learned_words_path(user.id)
        learned_words_path.parent.mkdir(parents=True, exist_ok=True)
        if not learned_words_path.exists():
            import json
            with open(learned_words_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "hindi_latin": [],
                    "hindi_devanagari": [],
                    "english": [],
                    "urdu": []
                }, f, indent=2, ensure_ascii=False)
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user."""
    schema = UserLoginSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    })


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user_id = get_current_user_id()
    
    # Check if user still exists and is active
    user = User.query.get(current_user_id)
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401
    
    access_token = create_access_token(identity=str(current_user_id))
    return jsonify({'access_token': access_token})


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile."""
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()})


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile."""
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    
    # Update allowed fields
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Profile update failed'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password."""
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    schema = PasswordChangeSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
    
    # Verify current password
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Validate new password strength
    is_valid, message = validate_password_strength(data['new_password'])
    if not is_valid:
        return jsonify({'error': message}), 400
    
    try:
        user.set_password(data['new_password'])
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Password change failed'}), 500


@auth_bp.route('/api-key', methods=['GET'])
@jwt_required()
def get_api_key():
    """Get user's API key."""
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'api_key': user.api_key})


@auth_bp.route('/api-key/regenerate', methods=['POST'])
@jwt_required()
def regenerate_api_key():
    """Regenerate user's API key."""
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        new_api_key = user.regenerate_api_key()
        db.session.commit()
        return jsonify({
            'message': 'API key regenerated successfully',
            'api_key': new_api_key
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"API key regeneration error: {str(e)}")
        return jsonify({'error': 'API key regeneration failed'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (mainly for completeness, JWT is stateless)."""
    return jsonify({'message': 'Logged out successfully'})


# API Key authentication decorator
def api_key_required(f):
    """Decorator to require API key authentication."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        user = User.query.filter_by(api_key=api_key, is_active=True).first()
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Add user to request context
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function
