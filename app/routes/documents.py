import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models import Document
from app import database
from config import Config
from app.utils import summarize_text

bp = Blueprint("documents", __name__)

@bp.route("/upload", methods = ["POST"])
@jwt_required()
def upload_document():
    if "file" not in request.files:
        return jsonify({"message": "No file path"}), 400
    file = request.files['file']

    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)

        new_document = Document(filename=filename, user_id=get_jwt_identity())
        database.session.add(new_document)
        database.session.commit()

        return jsonify({"message": "File uploaded successfully"}), 201

@bp.route('/documents', methods=['GET'])
@jwt_required()
def get_documents():
    user_id = get_jwt_identity()
    documents = Document.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": doc.id, "filename": doc.filename, "upload_date": doc.upload_date} for doc in documents]), 200

@bp.route('/<int:doc_id>/summarize', methods=['POST'])
@jwt_required()
def summarize_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    if document.user_id != get_jwt_identity():
        return jsonify({"msg": "Unauthorized"}), 403
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.filename)
    with open(file_path, 'r') as file:
        content = file.read()
    
    summary = summarize_text(content)
    return jsonify({"summary": summary}), 200

@bp.route('/<int:doc_id>/qa', methods=['POST'])
@jwt_required()
def answer_document_question(doc_id):
    document = Document.query.get_or_404(doc_id)
    if document.user_id != get_jwt_identity():
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.get_json()
    question = data.get('question')

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.filename)
    with open(file_path, 'r') as file:
        content = file.read()

    answer = answer_question(content, question)

    # Store the question-answer pair
    if document.qa_pairs:
        qa_pairs = json.loads(document.qa_pairs)
    else:
        qa_pairs = []
    qa_pairs.append({"question": question, "answer": answer})
    document.qa_pairs = json.dumps(qa_pairs)
    database.session.commit()

    return jsonify({"answer": answer}), 200

@bp.route('/<int:doc_id>/qa', methods=['GET'])
@jwt_required()
def get_document_qa_pairs(doc_id):
    document = Document.query.get_or_404(doc_id)
    if document.user_id != get_jwt_identity():
        return jsonify({"msg": "Unauthorized"}), 403

    if document.qa_pairs:
        qa_pairs = json.loads(document.qa_pairs)
        return jsonify(qa_pairs), 200
    else:
        return jsonify({"msg": "No question-answer pairs found for this document"}), 404
    
