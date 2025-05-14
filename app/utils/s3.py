import os
from werkzeug.datastructures import FileStorage
from app.extensions import s3_client

BUCKET = os.getenv('S3_BUCKET_NAME')

def upload_file_to_s3(file: FileStorage, key_prefix: str = "documents/") -> str:
    """
    Sube un file-like object a S3 y devuelve la URL pública.
    """
    filename = file.filename
    key = f"{key_prefix}{filename}"
    # Subimos el objeto SIN pasar ACL, ya que el bucket no las soporta
    s3_client.upload_fileobj(
        file,
        BUCKET,
        key
    )
    region = os.getenv('AWS_DEFAULT_REGION')
    return f"https://{BUCKET}.s3.{region}.amazonaws.com/{key}"
