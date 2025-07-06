from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from minio import Minio
from minio.error import S3Error
import io
import uuid
from typing import List
import logging

from app.core.config import settings
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Lazy MinIO client initialization
_minio_client = None

def get_minio_client():
    """Get or create MinIO client with lazy initialization"""
    global _minio_client
    if _minio_client is None:
        try:
            _minio_client = Minio(
                settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=False  # Set to True for HTTPS
            )
            
            # Ensure bucket exists
            if not _minio_client.bucket_exists(settings.minio_bucket):
                _minio_client.make_bucket(settings.minio_bucket)
                logger.info(f"Created MinIO bucket: {settings.minio_bucket}")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File storage service is not available"
            )
    
    return _minio_client

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a file to MinIO"""
    
    # Validate file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum size is 10MB."
        )
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
    unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
    
    # Read file content
    file_content = await file.read()
    
    try:
        minio_client = get_minio_client()
        
        # Upload to MinIO
        minio_client.put_object(
            bucket_name=settings.minio_bucket,
            object_name=unique_filename,
            data=io.BytesIO(file_content),
            length=len(file_content),
            content_type=file.content_type
        )
        
        # Generate download URL
        download_url = f"/api/v1/files/download/{unique_filename}"
        
        return {
            "filename": file.filename,
            "stored_filename": unique_filename,
            "size": len(file_content),
            "content_type": file.content_type,
            "download_url": download_url,
            "uploaded_by": current_user.id
        }
        
    except S3Error as e:
        logger.error(f"MinIO upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )

@router.get("/download/{filename}")
async def download_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Download a file from MinIO"""
    
    try:
        minio_client = get_minio_client()
        
        # Get object from MinIO
        obj = minio_client.get_object(settings.minio_bucket, filename)
        
        # Read object data
        data = obj.read()
        
        # Get object info for content type
        obj_stat = minio_client.stat_object(settings.minio_bucket, filename)
        
        return StreamingResponse(
            io.BytesIO(data),
            media_type=obj_stat.content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except S3Error as e:
        if e.code == "NoSuchKey":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        else:
            logger.error(f"MinIO download error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to download file: {str(e)}"
            )
    except Exception as e:
        logger.error(f"Unexpected download error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download file"
        )

@router.delete("/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a file from MinIO"""
    
    try:
        minio_client = get_minio_client()
        
        # Delete object from MinIO
        minio_client.remove_object(settings.minio_bucket, filename)
        
        return {"message": "File deleted successfully"}
        
    except S3Error as e:
        if e.code == "NoSuchKey":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        else:
            logger.error(f"MinIO delete error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
    except Exception as e:
        logger.error(f"Unexpected delete error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )

@router.get("/list")
async def list_files(
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """List files in MinIO bucket"""
    
    try:
        minio_client = get_minio_client()
        
        objects = minio_client.list_objects(settings.minio_bucket, recursive=True)
        
        files = []
        count = 0
        for obj in objects:
            if count >= limit:
                break
                
            files.append({
                "filename": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified.isoformat() if obj.last_modified else None
            })
            count += 1
        
        return {"files": files, "total": count}
        
    except S3Error as e:
        logger.error(f"MinIO list error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected list error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list files"
        ) 