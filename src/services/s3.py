"""
S3 service for document storage and retrieval.
"""
import boto3
from botocore.exceptions import ClientError
import os
import logging
from typing import Optional
import io

logger = logging.getLogger(__name__)

# AWS configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "caseintel-documents")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


class S3Service:
    """Service for interacting with S3 document storage."""
    
    def __init__(self):
        self.client = s3_client
        self.bucket = S3_BUCKET
    
    def upload_document(
        self,
        file_content: bytes,
        case_id: str,
        filename: str,
        content_type: str = "application/pdf"
    ) -> str:
        """
        Upload a document to S3.
        
        Args:
            file_content: Document content as bytes
            case_id: Case identifier
            filename: Original filename
            content_type: MIME type
            
        Returns:
            str: S3 key of uploaded document
        """
        try:
            key = f"cases/{case_id}/{filename}"
            
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_content,
                ContentType=content_type,
                ServerSideEncryption="AES256"
            )
            
            logger.info(f"Uploaded document to s3://{self.bucket}/{key}")
            return key
            
        except ClientError as e:
            logger.error(f"Failed to upload document: {str(e)}")
            raise
    
    def download_document(self, key: str) -> bytes:
        """
        Download a document from S3.
        
        Args:
            key: S3 key of the document
            
        Returns:
            bytes: Document content
        """
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            content = response["Body"].read()
            logger.info(f"Downloaded document from s3://{self.bucket}/{key}")
            return content
            
        except ClientError as e:
            logger.error(f"Failed to download document: {str(e)}")
            raise
    
    def download_from_url(self, url: str) -> bytes:
        """
        Download a document from a URL (S3 presigned URL or direct S3 URL).
        
        Args:
            url: Document URL
            
        Returns:
            bytes: Document content
        """
        try:
            # If it's an S3 URL, extract the key
            if "s3.amazonaws.com" in url or "s3://" in url:
                # Parse S3 key from URL
                if "s3://" in url:
                    key = url.replace(f"s3://{self.bucket}/", "")
                else:
                    # Extract key from HTTPS URL
                    parts = url.split(f"{self.bucket}/")
                    if len(parts) > 1:
                        key = parts[1].split("?")[0]  # Remove query params
                    else:
                        raise ValueError("Invalid S3 URL format")
                
                return self.download_document(key)
            else:
                # For non-S3 URLs, use requests
                import requests
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                return response.content
                
        except Exception as e:
            logger.error(f"Failed to download from URL: {str(e)}")
            raise
    
    def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate a presigned URL for document access.
        
        Args:
            key: S3 key of the document
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            str: Presigned URL
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expiration
            )
            logger.info(f"Generated presigned URL for {key}")
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise
    
    def delete_document(self, key: str) -> bool:
        """
        Delete a document from S3.
        
        Args:
            key: S3 key of the document
            
        Returns:
            bool: True if successful
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted document s3://{self.bucket}/{key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete document: {str(e)}")
            return False
    
    def list_case_documents(self, case_id: str) -> list[dict]:
        """
        List all documents for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            list: List of document metadata dicts
        """
        try:
            prefix = f"cases/{case_id}/"
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            
            documents = []
            for obj in response.get("Contents", []):
                documents.append({
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"],
                    "filename": obj["Key"].split("/")[-1]
                })
            
            logger.info(f"Listed {len(documents)} documents for case {case_id}")
            return documents
            
        except ClientError as e:
            logger.error(f"Failed to list documents: {str(e)}")
            return []


# Singleton instance
s3_service = S3Service()
