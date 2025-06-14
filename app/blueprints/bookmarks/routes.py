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
    
@bookmarks_bp.route('/toggle/<string:manga_id>', methods=['POST'])
@user_required
def toggle_bookmark(manga_id):
    existing = db.session.execute(
        select(Bookmark).where(
            (Bookmark.user_id == request.user_id) &
            (Bookmark.manga_id == manga_id)
        )
    ).scalar_one_or_none()
    
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'message': 'Bookmark removed'}), 200
    else:
        new_bookmark = Bookmark(user_id=request.user_id, manga_id=manga_id)
        db.session.add(new_bookmark)
        db.session.commit()
        return jsonify({'message': 'Bookmark added'}), 201
    
@bookmarks_bp.route("/", methods=['GET'])
def get_bookmarks():
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
@user_required
def get_bookmark_by_id(id):
    bookmark = db.session.get(Bookmark, id)
    
    if not bookmark:
        return jsonify({'message': 'Bookmark not found'}), 404
    
    if bookmark.user_id != request.user_id:
        return jsonify({'message': 'Forbidden: Can not get the bookmarks of another user'}), 403
    
    return jsonify(bookmark_schema.dump(bookmark)), 200

@bookmarks_bp.route('/user', methods=['GET'])
@user_required
def get_my_bookmarks():
    bookmarks = db.session.execute(
        select(Bookmark).where(Bookmark.user_id == request.user_id)
    ).scalars().all()
    
    return jsonify({'bookmarks': bookmarks_schema.dump(bookmarks)}), 200

@bookmarks_bp.route('/manga/<string:manga_id>', methods=['GET'])
@user_required
def get_bookmarks_for_manga(manga_id):
    bookmarks = db.session.execute(
        select(Bookmark).where(
            (Bookmark.manga_id == manga_id) &
            (Bookmark.user_id == request.user_id)
        )
    ).scalars().all()
    
    return jsonify({'bookmarks': bookmarks_schema.dump(bookmarks)}), 200

@bookmarks_bp.route('/<int:id>', methods=['PUT'])
@user_required
def update_bookmark(id):
    bookmark = db.session.get(Bookmark, id)
    
    if not bookmark:
        return jsonify({'message': 'Bookmark not found'}), 404
    
    if bookmark.user_id != request.user_id:
        return jsonify({'message': 'Forbidden: You do not own this bookmark'}), 403
    
    try:
        bookmark = bookmark_schema.load(request.json, instance=bookmark, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    db.session.commit()
    return bookmark_schema.jsonify(bookmark), 200

@bookmarks_bp.route('/<int:id>', methods=['DELETE'])
@user_required
def delete_bookmark(id):
    bookmark = db.session.get(Bookmark, id)
    
    if not bookmark:
        return jsonify({'message': 'Bookmark not found'}), 404
    
    if bookmark.user_id != request.user_id:
        return jsonify({'message': 'Forbidden: You can not delete another users bookmarks'}), 403
    
    db.session.delete(bookmark)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted bookmark {id}"}), 200