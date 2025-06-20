from .schema import download_schema, downloads_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Download, db
from . import downloads_bp
from app.utils.util import user_required, admin_required

@downloads_bp.route('/', methods=['POST'])
@user_required
def create_download():
    try:
        data = request.json
        data['user_id'] = request.user_id
        download_data = download_schema.load(data)
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    
    already_downloaded = db.session.execute(
        select(Download).where(
            (Download.chapter_id == download_data.chapter_id) &
            (Download.user_id == request.user_id)
        )
    ).scalar_one_or_none()
    
    if already_downloaded:
        return jsonify({
            'status': 'fail',
            'message': 'Already downloaded'
        }), 409
        
    try:
        db.session.add(download_data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Database error', 'error': str(e)}), 500
    
    return jsonify({'message': 'Downloaded successfully', 'download': download_schema.dump(download_data)}), 201

@downloads_bp.route('/', methods=['GET'])
@admin_required
def get_all_downloaded():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page
        total_count = db.session.query(Download).count()
        
        query = select(Download).offset(offset).limit(per_page)
        downloads = db.session.execute(query).scalars().all()
        
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_downloads': total_count,
            'downloads': downloads_schema.dump(downloads)
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching downloads', 'error': str(e)}), 500
    
@downloads_bp.route('/<int:id>', methods=['PUT'])
@user_required
def update_download(id):
    download = db.session.get(Download, id)
    
    if not download:
        return jsonify({'message': 'Download not found'}), 404
    
    if download.user_id != request.user_id:
        return jsonify({'message': 'Forbidden'}), 403
    
    try:
        request.json['user_id'] = request.user_id
        download = download_schema.load(request.json, instance=download)
    except ValidationError as e:
        return jsonify({e.messages}), 400
    
    db.session.commit()
    return jsonify(download_schema.dump(download)), 200

@downloads_bp.route('/<int:id>', methods=['DELETE'])
@user_required
def delete_download(id):
    download = db.session.get(Download, id)
    
    if not download:
        return jsonify({'message': 'Download not found'}), 404
    
    if download.user_id != request.user_id:
        return jsonify({'message': 'Forbidden'}), 403
    
    db.session.delete(download)
    db.session.commit()
    return jsonify({'message': f'successfully deleted download {id}'})