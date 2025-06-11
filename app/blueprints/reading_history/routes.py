from .schema import reading_histories_schema, reading_history_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import ReadingHistory, db
from . import reading_history_bp
from datetime import datetime
from app.utils.util import user_required, admin_required

@reading_history_bp.route('/', methods=['GET'])
@admin_required
def get_reading_history():
    query = select(ReadingHistory)
    reading_history = db.session.execute(query).scalars().all()
    
    return jsonify({'reading_history': reading_histories_schema.dump(reading_history)}), 200

@reading_history_bp.route('/admin/user/<string:user_id>', methods=['GET'])
@admin_required
def get_user_reading_history_admin(user_id):
    query = select(ReadingHistory).where(ReadingHistory.user_id == user_id)
    reading_history = db.session.execute(query).scalars().all()
    
    return jsonify({'reading_history': reading_histories_schema.dump(reading_history)}), 200

@reading_history_bp.route('/user', methods=['GET'])
@user_required
def get_reading_history_for_user():
    user_id = request.user_id
    
    query = select(ReadingHistory).where(ReadingHistory.user_id == user_id)
    reading_history = db.session.execute(query).scalars().all()
    
    return jsonify({'reading_history': reading_histories_schema.dump(reading_history)}), 200

@reading_history_bp.route('/user/<string:user_id>', methods=['PUT'])
@user_required
def update_reading_history(user_id):
    if request.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    manga_id = data.get('manga_id')
    last_chapter = data.get('last_chapter')
    
    if not manga_id or not last_chapter:
        return jsonify({'message': 'manga_id and last chapter are required'}), 400
    
    history = db.session.execute(
        select(ReadingHistory).where(
            (ReadingHistory.user_id == user_id)&
            (ReadingHistory.manga_id == manga_id)
        )
    ).scalar_one_or_none()
    
    if not history:
        return jsonify({'message': 'Reading history not found'}), 404
    
    history.last_chapter = last_chapter
    history.last_read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Reading history updated', 'reading history': reading_history_schema.dump(history)}), 200

@reading_history_bp.route('/admin/user/<string:user_id>', methods=['DELETE'])
@admin_required
def delete_user_history_admin(user_id):
    histories = db.session.execute(
        select(ReadingHistory).where(ReadingHistory.user_id == user_id)
    ).scalars().all()
    
    if not histories:
        return jsonify({'message': 'No reading history to delete'}), 404
    
    for history in histories:
        db.session.delete(history)
        
    db.session.commit()
    return jsonify({'message': f"Deleted reading history for user {user_id}"}), 200


@reading_history_bp.route('/user/<string:id>', methods=['DELETE'])
@user_required
def delete_reading_history(user_id):
    user_id = request.user_id
    
    if user_id != id:
        return jsonify({'message': 'Unauthorized to delete another user\'s history'}), 403
    
    histories = db.session.execute(
        select(ReadingHistory).where(ReadingHistory.user_id == user_id)
    ).scalars().all()
    
    if not histories:
        return jsonify({'message': 'No reading history to delete'}), 404
    
    for history in histories:
        db.session.delete(history)
        
    db.session.commit()
    return jsonify({'message': f"Successfully deleted user {id}'s reading history"}), 200