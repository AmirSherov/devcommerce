import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class S3PortfolioService:
    """Service for managing portfolio files in S3"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    def upload_file(self, file_key: str, content: str, content_type: str = 'text/plain') -> bool:
        """Upload file content to S3"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=content.encode('utf-8'),
                ContentType=f"{content_type}; charset=utf-8",
                CacheControl='max-age=86400',
                ContentEncoding='utf-8'
            )
            logger.info(f"Successfully uploaded {file_key} to S3")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload {file_key} to S3: {e}")
            return False
    
    def download_file(self, file_key: str) -> str:
        """Download file content from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            content = response['Body'].read().decode('utf-8')
            logger.info(f"Successfully downloaded {file_key} from S3")
            return content
        except ClientError as e:
            logger.error(f"Failed to download {file_key} from S3: {e}")
            return ""
    
    def delete_file(self, file_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            logger.info(f"Successfully deleted {file_key} from S3")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete {file_key} from S3: {e}")
            return False
    
    def delete_portfolio_folder(self, folder_path: str) -> bool:
        """Delete entire portfolio folder from S3"""
        try:
            # List all objects in the folder
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=folder_path
            )
            
            if 'Contents' in response:
                # Delete all objects in the folder
                objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
                
                self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects_to_delete}
                )
                
                logger.info(f"Successfully deleted portfolio folder {folder_path} from S3")
            
            return True
        except ClientError as e:
            logger.error(f"Failed to delete portfolio folder {folder_path} from S3: {e}")
            return False
    
    def create_portfolio_files(self, portfolio) -> bool:
        """Create all portfolio files in S3"""
        try:
            # Create full HTML document for public viewing
            full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{portfolio.title}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    {portfolio.html_content}
    <script src="script.js"></script>
</body>
</html>"""
            
            # Upload full HTML file
            html_success = self.upload_file(
                portfolio.html_file_key,
                full_html,
                'text/html'
            )
            
            # Upload CSS file (as is)
            css_success = self.upload_file(
                portfolio.css_file_key,
                portfolio.css_content,
                'text/css'
            )
            
            # Upload JS file (as is)
            js_success = self.upload_file(
                portfolio.js_file_key,
                portfolio.js_content,
                'application/javascript'
            )
            
            return html_success and css_success and js_success
        except Exception as e:
            logger.error(f"Failed to create portfolio files for {portfolio.title}: {e}")
            return False
    
    def update_portfolio_file(self, file_key: str, content: str, file_type: str) -> bool:
        """Update specific portfolio file in S3"""
        content_type_map = {
            'html': 'text/html',
            'css': 'text/css',
            'js': 'application/javascript'
        }
        
        content_type = content_type_map.get(file_type, 'text/plain')
        return self.upload_file(file_key, content, content_type)
    
    def sync_portfolio_to_s3(self, portfolio) -> bool:
        """Sync all portfolio content to S3"""
        try:
            # Create full HTML document for public viewing
            full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{portfolio.title}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    {portfolio.html_content}
    <script src="script.js"></script>
</body>
</html>"""
            
            # Upload full HTML file
            html_success = self.update_portfolio_file(
                portfolio.html_file_key,
                full_html,
                'html'
            )
            
            # Upload CSS file (as is)
            css_success = self.update_portfolio_file(
                portfolio.css_file_key,
                portfolio.css_content,
                'css'
            )
            
            # Upload JS file (as is)
            js_success = self.update_portfolio_file(
                portfolio.js_file_key,
                portfolio.js_content,
                'js'
            )
            
            return html_success and css_success and js_success
        except Exception as e:
            logger.error(f"Failed to sync portfolio {portfolio.title} to S3: {e}")
            return False
    
    def get_file_url(self, file_key: str) -> str:
        """Get public URL for file"""
        return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_key}"
    
    def file_exists(self, file_key: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError:
            return False


# Global instance
s3_service = S3PortfolioService() 