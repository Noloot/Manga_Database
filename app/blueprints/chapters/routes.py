from .schema import chapter_schema, chapters_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, and_
from app.models import Chapter, db, ReadingHistory
from . import chapters_bp
from app.utils.util import user_required, admin_required
from datetime import datetime, timezone

@chapters_bp.route('/', methods=['POST'])
@admin_required
def create_chapter():
    try:
        chapter_data = chapter_schema.load(request.json)
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    
    existing_chapter = db.session.execute(select(Chapter).where(
        and_(
            Chapter.chapter_number == chapter_data.chapter_number,
            Chapter.manga_id == chapter_data.manga_id
        )
    )).scalar_one_or_none()
    
    if existing_chapter:
        return jsonify({
            "status": "fail",
            "message": "Chapter already exists"
        }), 409
        
    try:
        db.session.add(chapter_data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Database error', 'error': str(e)}), 500
    
    return jsonify({'message': 'New chapter added successfully', 'chapter': chapter_schema.dump(chapter_data)}), 201

@chapters_bp.route("/", methods=['GET'])
def get_chapter():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page
        total_count = db.session.query(Chapter).count()
        
        query = select(Chapter).offset(offset).limit(per_page)
        chapters = db.session.execute(query).scalars().all()
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_chapters': total_count,
            'chapters': chapters_schema.dump(chapters)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching Chapters', 'error': str(e)}), 500
    
@chapters_bp.route('/<string:id>', methods=['GET'])
@user_required
def get_chapter_by_id(id):
    chapter = db.session.get(Chapter, id)
    if not chapter:
        return jsonify({'message': 'Chapter not found'}), 404
    
    user_id = request.user_id
    
    if user_id:
        history = db.session.execute(
            select(ReadingHistory).where(
                (ReadingHistory.user_id == user_id) &
                (ReadingHistory.manga_id == chapter.manga_id)
            )
        ).scalar_one_or_none()
        
        if not history:
            history = ReadingHistory(
                user_id=user_id, 
                manga_id=chapter.manga_id,
                last_chapter=chapter.id
            )
            db.session.add(history)
        else:
            history.last_chapter = chapter.id
            history.last_read_at = datetime.now(timezone.utc)
            
        db.session.commit()
            
    return jsonify(chapter_schema.dump(chapter)), 200
    
@chapters_bp.route('/manga/<int:manga_id>', methods=['GET'])
def get_chapters_by_manga_id(manga_id):
    chapters = db.session.execute(
        select(Chapter).where(Chapter.manga_id == manga_id)
    ).scalars().all()
    
    if not chapters:
        return jsonify({'message': 'No chapters found for this manga'}), 404
    
    return jsonify(chapters_schema.dump(chapters)), 200

@chapters_bp.route('/search', methods=['GET'])
def search_for_chapter():
    title = request.args.get('title')
    language = request.args.get('language')
    
    query = select(Chapter)
    if title:
        query = query.where(Chapter.title.ilike(f"%{title}%"))
    if language:
        query = query.where(Chapter.language == language)
        
    results = db.session.execute(query).scalars().all()
    return jsonify(chapters_schema.dump(results)), 200

@chapters_bp.route('/<string:id>/next', methods=['GET'])
def get_next_chapter(id):
    chapter = db.session.get(Chapter, id)
    if not chapter:
        return jsonify({'message': 'Chapter not found'}), 404
    
    next_chapter = db.session.execute(select(Chapter).where(Chapter.manga_id == chapter.manga_id, Chapter.release_date > chapter.release_date).order_by(Chapter.release_date.asc())).scalars().first()
    
    if not next_chapter:
        return jsonify({'message': 'No next chapter'})
    
    return jsonify(chapter_schema.dump(next_chapter)), 200

@chapters_bp.route('/<string:id>', methods=['PUT'])
@admin_required
def update_chapter_by_id(id):
    chapter = db.session.get(Chapter, id)
    
    if not chapter:
        return jsonify({'message': 'Chapter not found'}), 404
    
    try:
        chapter = chapter_schema.load(request.json, instance=chapter)
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    
    db.session.commit()
    return jsonify(chapter_schema.dump(chapter)), 200

@chapters_bp.route('/<string:id>', methods=['DELETE'])
@admin_required
def delete_chapter(id):
    chapter = db.session.get(Chapter, id)
    
    if not chapter:
        return jsonify({'message': 'Chapter not found'}), 404
    
    db.session.delete(chapter)
    db.session.commit()
    return jsonify({'message': f'successfully deleted chapter {id}'}), 200