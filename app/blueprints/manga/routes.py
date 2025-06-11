from .schema import manga_schema, mangas_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Manga, db
from . import manga_bp

@manga_bp.route("/", methods=['POST'])
def create_manga():
    try:
        manga_data = manga_schema.load(request.json)
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    
    manga_existing = db.session.execute(select(Manga).where(Manga.title == manga_data.title, Manga.author == manga_data.author)).scalar_one_or_none()
    
    if manga_existing:
        return jsonify({
            "status": "fail",
            "message": "Manga already exists"
        }), 409
        
    try:
        db.session.add(manga_data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Database error', 'error': str(e)}), 500
    
    return jsonify({'message': 'New manga added successfully', 'manga': manga_schema.dump(manga_data)}), 201

@manga_bp.route('/', methods=['GET'])
def get_mangas():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 100))
        offset = (page - 1) * per_page
        total_count = db.session.query(Manga).count()
        
        query = select(Manga).offset(offset).limit(per_page)
        mangas = db.session.execute(query).scalars().all()
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_mangas': total_count,
            'mangas': mangas_schema.dump(mangas)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching Mangas', 'error': str(e)}), 500
    
@manga_bp.route('/<int:id>', methods=['GET'])
def get_manga_by_id(id):
    query = select(Manga).where(Manga.id == id)
    result = db.session.execute(query).scalars().first()
    
    if result is None:
        return jsonify({'message': 'Manga is not found'}), 404
    
    return jsonify(manga_schema.dump(result)), 200

@manga_bp.route('<int:id>', methods=['PUT'])
def update_manga(id):
    manga = db.session.get(Manga, id)
    
    if not manga:
        return jsonify({'messaga': 'Manga not found'}), 404
    
    try:
        manga = manga_schema.load(request.json, instance=manga, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    db.session.commit()
    return manga_schema.jsonify(manga), 200

@manga_bp.route('<int:id>', methods=['DELETE'])
def delete_manga(id):
    manga = db.session.get(Manga, id)
    
    if not manga:
        return jsonify({'message': 'Manga not found'}), 404
    
    db.session.delete(manga)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted manga {id}"}), 200