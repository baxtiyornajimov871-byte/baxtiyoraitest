"""
BaxtiyorAiTest - Upload Service
Secure file upload handling, processing, and management
"""

import os
from werkzeug.utils import secure_filename
from uuid import uuid4
from PIL import Image
import PyPDF2
from docx import Document

from app.extensions import db
from app.models.upload import Upload
from app.config import Config


class UploadService:
    """Secure File Upload & Processing Service"""

    ALLOWED_EXTENSIONS = {
        'image': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
        'document': ['.pdf', '.txt', '.docx', '.doc'],
        'audio': ['.mp3', '.wav', '.ogg']
    }

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    @staticmethod
    def allowed_file(filename: str, file_type: str = None) -> bool:
        """Check if file extension is allowed"""
        if not filename:
            return False
        ext = os.path.splitext(filename)[1].lower()
        
        if file_type and file_type in UploadService.ALLOWED_EXTENSIONS:
            return ext in UploadService.ALLOWED_EXTENSIONS[file_type]
        
        # Check all types
        for extensions in UploadService.ALLOWED_EXTENSIONS.values():
            if ext in extensions:
                return True
        return False

    @staticmethod
    def save_upload(file, user_id: int, conversation_id: int = None):
        """Save uploaded file securely"""
        if not file or not file.filename:
            raise ValueError("No file provided")

        if len(file.read()) > UploadService.MAX_FILE_SIZE:
            file.seek(0)
            raise ValueError("File too large. Maximum size is 50MB")
        file.seek(0)

        if not UploadService.allowed_file(file.filename):
            raise ValueError("File type not allowed")

        # Create secure filename
        original_filename = file.filename
        ext = os.path.splitext(original_filename)[1].lower()
        secure_name = f"{uuid4().hex}{ext}"
        
        # Create upload path
        upload_dir = os.path.join(Config.UPLOAD_FOLDER, str(user_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, secure_name)
        file.save(filepath)

        # Get file size
        file_size = os.path.getsize(filepath)

        # Create database record
        upload = Upload(
            user_id=user_id,
            conversation_id=conversation_id,
            original_filename=original_filename,
            file_path=filepath,
            file_size=file_size,
            file_type=file.content_type or "application/octet-stream"
        )
        upload.save()

        # Process file in background (extract text, generate preview)
        UploadService.process_upload_async(upload.id)

        return upload

    @staticmethod
    def process_upload_async(upload_id: int):
        """Process uploaded file (extract text, generate preview)"""
        upload = Upload.query.get(upload_id)
        if not upload:
            return

        try:
            ext = upload.file_extension

            if ext in ['.pdf']:
                text = UploadService.extract_pdf_text(upload.file_path)
            elif ext in ['.docx']:
                text = UploadService.extract_docx_text(upload.file_path)
            elif ext in ['.txt']:
                with open(upload.file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
                UploadService.create_image_preview(upload.file_path, upload.id)
                text = None
            else:
                text = None

            upload.mark_as_processed(extracted_text=text)
            
        except Exception as e:
            upload.mark_as_failed(str(e))

    @staticmethod
    def extract_pdf_text(file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    @staticmethod
    def extract_docx_text(file_path: str) -> str:
        """Extract text from DOCX"""
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    @staticmethod
    def create_image_preview(file_path: str, upload_id: int):
        """Create thumbnail for images"""
        try:
            img = Image.open(file_path)
            img.thumbnail((400, 400))
            
            preview_dir = os.path.join(Config.UPLOAD_FOLDER, "previews")
            os.makedirs(preview_dir, exist_ok=True)
            
            preview_path = os.path.join(preview_dir, f"thumb_{upload_id}.jpg")
            img.save(preview_path, "JPEG", quality=85)
            
            # Update upload with preview URL
            upload = Upload.query.get(upload_id)
            if upload:
                upload.preview_url = f"/static/uploads/previews/thumb_{upload_id}.jpg"
                db.session.commit()
        except:
            pass  # Silently fail preview generation

    @staticmethod
    def get_user_uploads(user_id: int, limit=20):
        """Get user's uploaded files"""
        return Upload.query.filter_by(user_id=user_id, is_deleted=False)\
                          .order_by(Upload.created_at.desc()).limit(limit).all()

    @staticmethod
    def delete_upload(upload_id: int, user_id: int):
        """Soft delete upload"""
        upload = Upload.query.filter_by(id=upload_id, user_id=user_id).first()
        if not upload:
            raise ValueError("Upload not found")
        
        upload.soft_delete()
        return True

    @staticmethod
    def get_upload_by_id(upload_id: int, user_id: int = None):
        """Get single upload with permission check"""
        upload = Upload.query.get(upload_id)
        if not upload:
            return None
        if user_id and upload.user_id != user_id:
            return None
        return upload