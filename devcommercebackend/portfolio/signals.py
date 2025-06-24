from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Portfolio
from .s3_service import s3_service
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(pre_delete, sender=Portfolio)
def delete_portfolio_files_from_s3(sender, instance, **kwargs):
    """Delete portfolio files from S3 when portfolio is deleted"""
    try:
        # Delete entire portfolio folder from S3
        success = s3_service.delete_portfolio_folder(instance.s3_folder_path)
        if success:
            logger.info(f"Successfully deleted S3 files for portfolio: {instance.title}")
        else:
            logger.error(f"Failed to delete S3 files for portfolio: {instance.title}")
    except Exception as e:
        logger.error(f"Error deleting S3 files for portfolio {instance.title}: {e}")


@receiver(pre_delete, sender=User)
def delete_user_portfolio_files_from_s3(sender, instance, **kwargs):
    """Delete all user's portfolio files from S3 when user is deleted"""
    try:
        # Get all user's portfolios
        user_portfolios = Portfolio.objects.filter(author=instance)
        
        for portfolio in user_portfolios:
            # Delete each portfolio's S3 files
            success = s3_service.delete_portfolio_folder(portfolio.s3_folder_path)
            if success:
                logger.info(f"Successfully deleted S3 files for portfolio: {portfolio.title}")
            else:
                logger.error(f"Failed to delete S3 files for portfolio: {portfolio.title}")
        
        # Also try to delete the entire user folder
        user_folder_path = f"portfolios/{instance.username}/"
        s3_service.delete_portfolio_folder(user_folder_path)
        logger.info(f"Deleted S3 folder for user: {instance.username}")
        
    except Exception as e:
        logger.error(f"Error deleting S3 files for user {instance.username}: {e}") 