"""
Unified notification system for email and Discord alerts.

This module provides a centralized notification system that supports:
- Email alerts via SMTP
- Discord alerts via webhooks
- Unified interface for sending alerts to multiple channels
"""

import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List
import requests
from .logger import get_logger

logger = get_logger(__name__)


class EmailNotifier:
    """Handle email notifications via SMTP"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, 
                 password: str, from_email: str, to_emails: List[str], enabled: bool = True):
        """
        Initialize email notifier.
        
        Args:
            smtp_server: SMTP server address (e.g., smtp.gmail.com)
            smtp_port: SMTP port (usually 587 for TLS)
            username: SMTP username
            password: SMTP password or app password
            from_email: Sender email address
            to_emails: List of recipient email addresses
            enabled: Whether email notifications are enabled
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
        self.enabled = enabled
        
        logger.info(
            "email_notifier_initialized",
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            enabled=enabled,
            recipients=len(to_emails)
        )
    
    def _create_html_email(self, subject: str, message: str, alert_type: str = "info") -> str:
        """
        Create HTML formatted email.
        
        Args:
            subject: Email subject
            message: Alert message (supports markdown-style formatting)
            alert_type: Type of alert (info, success, warning, error)
            
        Returns:
            HTML formatted email body
        """
        # Color scheme based on alert type
        color_map = {
            "info": "#3498DB",      # Blue
            "success": "#33FF57",   # Green
            "warning": "#FFA500",   # Orange
            "error": "#FF0000",     # Red
            "neutral": "#808080"    # Gray
        }
        
        color = color_map.get(alert_type, "#3498DB")
        
        # Convert markdown-style bold to HTML
        html_message = message.replace("**", "<strong>").replace("**", "</strong>")
        html_message = html_message.replace("\n", "<br>")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 20px;
                    max-width: 600px;
                    margin: 0 auto;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    background-color: {color};
                    color: white;
                    padding: 15px;
                    border-radius: 8px 8px 0 0;
                    margin: -20px -20px 20px -20px;
                }}
                .content {{
                    color: #333;
                    line-height: 1.6;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #999;
                    font-size: 12px;
                    text-align: center;
                }}
                strong {{
                    color: {color};
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔔 Trading Alert - {subject}</h2>
                </div>
                <div class="content">
                    <p>{html_message}</p>
                </div>
                <div class="footer">
                    <p>Zerodha Trading Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def send_email(self, subject: str, message: str, alert_type: str = "info") -> bool:
        """
        Send email notification.
        
        Args:
            subject: Email subject
            message: Alert message
            alert_type: Type of alert (info, success, warning, error)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("email_disabled", subject=subject)
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[Trading Alert] {subject}"
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            
            # Create plain text and HTML versions
            text_part = MIMEText(message, 'plain')
            html_part = MIMEText(self._create_html_email(subject, message, alert_type), 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(
                "email_sent",
                subject=subject,
                recipients=len(self.to_emails),
                alert_type=alert_type
            )
            return True
            
        except Exception as e:
            logger.error(
                "email_send_failed",
                error=str(e),
                subject=subject,
                exc_info=True
            )
            return False
    
    def send_test_email(self) -> bool:
        """Send a test email to verify configuration"""
        return self.send_email(
            subject="Test Alert",
            message="**Status:** Test email from Trading Bot\n**Time:** " + 
                   datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                   "\n\nIf you receive this, email notifications are working correctly!",
            alert_type="info"
        )


class DiscordNotifier:
    """Handle Discord webhook notifications"""
    
    def __init__(self, webhook_url: str, enabled: bool = True):
        """
        Initialize Discord notifier.
        
        Args:
            webhook_url: Discord webhook URL
            enabled: Whether Discord notifications are enabled
        """
        self.webhook_url = webhook_url
        self.enabled = enabled
        
        logger.info(
            "discord_notifier_initialized",
            enabled=enabled,
            webhook_configured=bool(webhook_url)
        )
    
    def send_alert(self, title: str, message: str, color: int = 0xFF5733) -> bool:
        """
        Send Discord webhook alert.
        
        Args:
            title: Alert title
            message: Alert message
            color: Embed color (hex integer)
            
        Returns:
            True if alert sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("discord_disabled", title=title)
            return False
        
        if not self.webhook_url:
            logger.warning("discord_webhook_not_configured")
            return False
        
        try:
            embed = {
                "embeds": [{
                    "title": f"🔔 {title}",
                    "description": message,
                    "color": color,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Zerodha Trading Bot"}
                }]
            }
            
            response = requests.post(self.webhook_url, json=embed, timeout=5)
            
            if response.status_code == 204:
                logger.info("discord_alert_sent", title=title, status="success")
                return True
            else:
                logger.warning(
                    "discord_alert_failed",
                    title=title,
                    status_code=response.status_code
                )
                return False
                
        except Exception as e:
            logger.error(
                "discord_alert_error",
                error=str(e),
                title=title,
                exc_info=True
            )
            return False
    
    def send_test_alert(self) -> bool:
        """Send a test alert to verify configuration"""
        return self.send_alert(
            title="Test Alert",
            message="**Status:** Test alert from Trading Bot\n**Time:** " + 
                   datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                   "\n\nIf you receive this, Discord notifications are working correctly!",
            color=0x3498DB
        )


class NotificationManager:
    """Unified notification manager for all alert channels"""
    
    def __init__(self, email_notifier: Optional[EmailNotifier] = None,
                 discord_notifier: Optional[DiscordNotifier] = None):
        """
        Initialize notification manager.
        
        Args:
            email_notifier: EmailNotifier instance (optional)
            discord_notifier: DiscordNotifier instance (optional)
        """
        self.email_notifier = email_notifier
        self.discord_notifier = discord_notifier
        
        logger.info(
            "notification_manager_initialized",
            email_enabled=email_notifier is not None and email_notifier.enabled,
            discord_enabled=discord_notifier is not None and discord_notifier.enabled
        )
    
    def _map_color_to_alert_type(self, color: int) -> str:
        """Map Discord color to email alert type"""
        color_map = {
            0x3498DB: "info",      # Blue
            0x33FF57: "success",   # Green
            0xFF5733: "error",     # Red/Orange
            0xFF0000: "error",     # Red
            0xFFA500: "warning",   # Orange
            0x808080: "neutral"    # Gray
        }
        return color_map.get(color, "info")
    
    def send_alert(self, message: str, title: str = "RSI Alert", 
                   color: int = 0xFF5733, async_send: bool = True) -> None:
        """
        Send alert to all enabled notification channels.
        
        Args:
            message: Alert message
            title: Alert title
            color: Color code (used for Discord and email styling)
            async_send: If True, send notifications in background thread
        """
        def _send():
            alert_type = self._map_color_to_alert_type(color)
            
            # Send to email
            if self.email_notifier and self.email_notifier.enabled:
                self.email_notifier.send_email(
                    subject=title,
                    message=message,
                    alert_type=alert_type
                )
            
            # Send to Discord
            if self.discord_notifier and self.discord_notifier.enabled:
                self.discord_notifier.send_alert(
                    title=title,
                    message=message,
                    color=color
                )
        
        if async_send:
            # Send in background to avoid blocking GUI
            threading.Thread(target=_send, daemon=True).start()
        else:
            _send()
    
    def send_test_alerts(self) -> dict:
        """
        Send test alerts to all configured channels.
        
        Returns:
            Dictionary with test results for each channel
        """
        results = {}
        
        if self.email_notifier:
            results['email'] = self.email_notifier.send_test_email()
        
        if self.discord_notifier:
            results['discord'] = self.discord_notifier.send_test_alert()
        
        logger.info("test_alerts_sent", results=results)
        return results


def create_notification_manager_from_config() -> NotificationManager:
    """
    Create NotificationManager from environment configuration.
    
    Returns:
        Configured NotificationManager instance
    """
    from .config import Config
    import os
    
    # Email configuration
    email_notifier = None
    email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
    
    if email_enabled:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        email_from = os.getenv('EMAIL_FROM', smtp_username)
        email_to = os.getenv('EMAIL_TO', '')
        email_to_additional = os.getenv('EMAIL_TO_ADDITIONAL', '')
        
        # Build recipient list
        to_emails = [e.strip() for e in email_to.split(',') if e.strip()]
        if email_to_additional:
            to_emails.extend([e.strip() for e in email_to_additional.split(',') if e.strip()])
        
        if smtp_username and smtp_password and to_emails:
            email_notifier = EmailNotifier(
                smtp_server=smtp_server,
                smtp_port=smtp_port,
                username=smtp_username,
                password=smtp_password,
                from_email=email_from,
                to_emails=to_emails,
                enabled=True
            )
        else:
            logger.warning(
                "email_config_incomplete",
                has_username=bool(smtp_username),
                has_password=bool(smtp_password),
                has_recipients=bool(to_emails)
            )
    
    # Discord configuration
    discord_notifier = None
    discord_enabled = os.getenv('DISCORD_ENABLED', 'true').lower() == 'true'
    
    if discord_enabled:
        discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')
        
        if discord_webhook_url:
            discord_notifier = DiscordNotifier(
                webhook_url=discord_webhook_url,
                enabled=True
            )
        else:
            logger.warning("discord_webhook_not_configured")
    
    return NotificationManager(
        email_notifier=email_notifier,
        discord_notifier=discord_notifier
    )


if __name__ == "__main__":
    # Test the notification system
    print("Testing notification system...")
    
    manager = create_notification_manager_from_config()
    results = manager.send_test_alerts()
    
    print(f"\nTest Results:")
    for channel, success in results.items():
        status = "✓ Success" if success else "✗ Failed"
        print(f"  {channel}: {status}")
