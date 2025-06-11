from .schema import bookmark_schema, bookmarks_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, and_
from app.models import Bookmark, db
from . import bookmarks_bp
from werkzeug.security import check_password_hash
from app.utils.util import encode_token, user_required

@bookmarks_bp.route('/', methods=['POST'])
@user_required
def add_bookmark():
    try:
        data = request.json
        data['user_id'] = request.user_id
        bookmark_data = bookmark_schema.load(data)
    except ValidationError as e:
        print("VALIDATION ERROR:", e.messages)
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    
    existing = db.session.execute(
        select(Bookmark).where(
            and_(
                Bookmark.user_id == request.user_id,
                Bookmark.manga_id == bookmark_data.manga_id
            )
        )
    ).scalar_one_or_none()
    
    if existing:
        return jsonify({'message': 'Bookmark already exists'}), 409
    
    db.session.add(bookmark_data)
    db.session.commit()
    return jsonify({
        'message': 'Bookmark added successfully',
        'bookmark': bookmark_schema.dump(bookmark_data)
    }), 201
    
@bookmarks_bp.route("/", methods=['GET'])
def get_bookmars():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page
        total_count = db.session.query(Bookmark).count()
        
        query = select(Bookmark).offset(offset).limit(per_page)
        bookmarks = db.session.execute(query).scalars().all()
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_bookmarks': total_count,
            'bookmarks': bookmarks_schema.dump(bookmarks)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching Bookmarks', 'error': str(e)}), 500
    
@bookmarks_bp.route('/<int:id>', methods=['GET'])
def get_bookmark_by_id(id):
    query = select(Bookmark).where(Bookmark.id == id)
    result = db.session.execute(query).scalars().first()
    
    if result is None:
        return jsonify({'message': 'Bookmark not found'}), 404
    
    return jsonify(bookmark_schema.dump(result)), 200

@bookmarks_bp.route('/<int:id>', methods=['PUT'])
def update_bookmark(id):
    bookmark = db.session.get(Bookmark, id)
    
    if not bookmark:
        return jsonify({'message': 'Bookmark not found'}), 404
    
    try:
        bookmark = bookmark_schema.load(request.json, instance=bookmark, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    db.session.commit()
    return bookmark_schema.jsonify(bookmark), 200

@bookmarks_bp.route('/<int:id>', methods=['DELETE'])
def delete_bookmark(id):
    bookmark = db.session.get(Bookmark, id)
    
    if not bookmark:
        return jsonify({'message': 'Bookmark not found'}), 404
    
    db.session.delete(bookmark)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted bookmark {id}"}), 200