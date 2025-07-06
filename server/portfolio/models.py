from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import uuid

User = get_user_model()


class Portfolio(models.Model):
    """Portfolio project model with S3 file storage"""
    
    # Basic info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    slug = models.SlugField(max_length=255, blank=True, unique=True)  # Уникальный глобально для субдоменов
    
    # Content is now stored directly in database (no S3)
    
    # Portfolio content
    html_content = models.TextField(default='<div class="container">\n    <h1 id="title">Привет, мир!</h1>\n    <p>Это мой первый проект портфолио.</p>\n    <button id="clickBtn">Нажми меня!</button>\n</div>')
    css_content = models.TextField(default='/* Ваши CSS стили */\n.container {\n    font-family: \'Arial\', sans-serif;\n    max-width: 800px;\n    margin: 0 auto;\n    padding: 20px;\n    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n    min-height: 100vh;\n    display: flex;\n    flex-direction: column;\n    justify-content: center;\n    align-items: center;\n    color: white;\n}\n\nh1 {\n    font-size: 3rem;\n    margin-bottom: 1rem;\n    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);\n}\n\np {\n    font-size: 1.2rem;\n    line-height: 1.6;\n    margin-bottom: 2rem;\n    text-align: center;\n}\n\nbutton {\n    background: white;\n    color: #667eea;\n    border: none;\n    padding: 12px 24px;\n    font-size: 1rem;\n    border-radius: 25px;\n    cursor: pointer;\n    transition: all 0.3s ease;\n    font-weight: bold;\n}\n\nbutton:hover {\n    transform: translateY(-2px);\n    box-shadow: 0 5px 15px rgba(0,0,0,0.2);\n}')
    js_content = models.TextField(default='// JavaScript код\nconsole.log("Portfolio loaded!");\n\n// Ждем загрузки DOM\ndocument.addEventListener("DOMContentLoaded", function() {\n    console.log("DOM ready");\n    \n    const title = document.getElementById("title");\n    const button = document.getElementById("clickBtn");\n    \n    if (title) {\n        title.addEventListener("click", function() {\n            title.style.color = title.style.color === "yellow" ? "white" : "yellow";\n        });\n    }\n    \n    if (button) {\n        button.addEventListener("click", function() {\n            alert("Button clicked!");\n            button.textContent = "Works great!";\n        });\n    }\n});')
    
    # Metadata
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    
    # Tags
    tags = models.JSONField(default=list, blank=True)  # ['html', 'css', 'javascript', 'responsive']
    
    class Meta:
        ordering = ['-updated_at']
        # Slug должен быть уникальным глобально для субдоменов
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"
    
    def save(self, *args, **kwargs):
        # Auto-generate unique slug (globally unique for subdomains)
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            
            # Проверяем уникальность глобально, исключая текущий объект
            while Portfolio.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate that user doesn't exceed 5 portfolios limit"""
        if not self.pk:  # Only for new portfolios
            user_portfolio_count = Portfolio.objects.filter(author=self.author).count()
            if user_portfolio_count >= 5:
                raise ValidationError("Максимальное количество портфолио: 5")
    
    @property
    def public_url(self):
        """Get public URL for the portfolio (via Django subdomain)"""
        if self.is_public:
            from django.conf import settings
            if settings.DEBUG:
                return f"http://{self.slug}.localhost:8000/"
            else:
                return f"https://{self.slug}.devcommerce.org/"
        return None
    
    def get_file_urls(self):
        """Get URLs for portfolio content (for compatibility)"""
        if self.is_public:
            return {
                'html': self.public_url,
                'css': self.public_url, 
                'js': self.public_url,
            }
        return {
            'html': None,
            'css': None,
            'js': None,
        }


class PortfolioLike(models.Model):
    """Portfolio likes tracking"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolio_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['portfolio', 'user']
    
    def __str__(self):
        return f"{self.user.username} likes {self.portfolio.title}"


class PortfolioView(models.Model):
    """Portfolio views tracking"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolio_views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Anonymous views allowed
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['portfolio', 'ip_address']  # One view per IP per portfolio
    
    def __str__(self):
        return f"View of {self.portfolio.title} from {self.ip_address}"
