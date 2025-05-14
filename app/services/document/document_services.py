import os
from datetime import datetime
from app.extensions import db, s3_client
from app.models.document.document import Document
from app.utils.s3 import upload_file_to_s3

BUCKET = os.getenv('S3_BUCKET_NAME')
REGION = os.getenv('AWS_DEFAULT_REGION')

def format_document(doc: Document):
    return {
        "document_id": doc.document_id,
        "document_type": doc.document_type,
        "document_name": doc.document_name,
        "file_path":     doc.file_path,
        "created_at":    doc.created_at.isoformat(),
        "updated_at":    doc.updated_at.isoformat() if doc.updated_at else None,
    }

def get_all_documents():
    docs = Document.query.filter(Document.deleted_at == None).all()
    return [format_document(d) for d in docs]

def get_document_by_id(doc_id: int):
    d = Document.query.filter_by(document_id=doc_id, deleted_at=None).first()
    return format_document(d) if d else None

def create_document(file,document_name: str, document_type: int,key_prefix: str = "documents/"):
    """
    file: FileStorage
    document_type: 0=report,1=template,2=release_letter
    """
    # 1) Sube a S3 usando el prefijo que venga
    url = upload_file_to_s3(file, key_prefix)
    # 2) Crea registro en la BD
    doc = Document(
        document_type=document_type,
        document_name=document_name,
        file_path=url
    )
    db.session.add(doc)
    db.session.commit()
    return format_document(doc)

def delete_document(doc_id: int):
    doc = Document.query.filter_by(document_id=doc_id, deleted_at=None).first()
    if not doc:
        return False
    doc.deleted_at = datetime.utcnow()
    db.session.commit()
    return True

def update_document(doc_id: int, document_name: str | None = None,file=None, document_type=None, key_prefix: str = "documents/"):
    """
    Actualiza un Document:
      - Si recibe `file` (FileStorage), lo sube a S3 y actualiza file_path.
      - Si recibe `document_type`, lo actualiza.
    Devuelve el objeto formateado o None si no existe.
    """
    doc = Document.query.filter_by(document_id=doc_id, deleted_at=None).first()
    if not doc:
        return None

    if file:
        url = upload_file_to_s3(file, key_prefix)
        doc.file_path = url

    if document_type is not None:
        doc.document_type = document_type
    
    if document_name is not None:
        doc.document_name = document_name
    doc.updated_at = datetime.utcnow()

    db.session.commit()
    return format_document(doc)


def get_s3_stream_for_document(doc_id: int):
    """
    Recupera el stream, content_type y filename para el documento dado.
    """
    doc = Document.query.filter_by(document_id=doc_id, deleted_at=None).first()
    if not doc:
        return None

    # Extraemos la key (path dentro del bucket) a partir de la URL almacenada
    prefix = f"https://{BUCKET}.s3.{REGION}.amazonaws.com/"
    key = doc.file_path.replace(prefix, "")

    # Obtenemos el objeto de S3
    obj = s3_client.get_object(Bucket=BUCKET, Key=key)
    stream = obj["Body"]          # StreamingBody
    content_type = obj["ContentType"]
    filename = key.split("/")[-1]
    return stream, content_type, filename