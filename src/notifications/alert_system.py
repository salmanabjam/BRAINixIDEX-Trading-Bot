"""
Alert & Notification System
============================
Price alerts, signal notifications, Email/Telegram integration.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional, Literal
import json
from pathlib import Path
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

AlertType = Literal['price', 'signal', 'system', 'custom']
AlertPriority = Literal['low', 'medium', 'high', 'critical']


@dataclass
class Alert:
    """Alert data structure."""
    id: str
    type: AlertType
    priority: AlertPriority
    symbol: Optional[str]
    condition: str
    threshold: Optional[float]
    message: str
    created_at: datetime
    triggered_at: Optional[datetime] = None
    active: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.triggered_at:
            data['triggered_at'] = self.triggered_at.isoformat()
        return data


class AlertManager:
    """Manage alerts and notifications."""
    
    def __init__(self, config_path: str = "config/alerts.json"):
        """Initialize alert manager."""
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.alerts: List[Alert] = []
        self.load_alerts()
    
    def load_alerts(self):
        """Load saved alerts."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.alerts = [
                        Alert(
                            id=a['id'],
                            type=a['type'],
                            priority=a['priority'],
                            symbol=a.get('symbol'),
                            condition=a['condition'],
                            threshold=a.get('threshold'),
                            message=a['message'],
                            created_at=datetime.fromisoformat(
                                a['created_at']
                            ),
                            triggered_at=datetime.fromisoformat(
                                a['triggered_at']
                            ) if a.get('triggered_at') else None,
                            active=a.get('active', True)
                        )
                        for a in data
                    ]
            except Exception as e:
                logger.error(f"Failed to load alerts: {e}")
    
    def save_alerts(self):
        """Save alerts to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump([a.to_dict() for a in self.alerts], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")
    
    def create_alert(
        self,
        alert_type: AlertType,
        priority: AlertPriority,
        condition: str,
        message: str,
        symbol: Optional[str] = None,
        threshold: Optional[float] = None
    ) -> Alert:
        """Create new alert."""
        alert = Alert(
            id=f"alert_{datetime.now().timestamp()}",
            type=alert_type,
            priority=priority,
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            message=message,
            created_at=datetime.now()
        )
        self.alerts.append(alert)
        self.save_alerts()
        return alert
    
    def check_price_alert(self, symbol: str, current_price: float):
        """Check if price alerts should trigger."""
        for alert in self.alerts:
            if not alert.active or alert.type != 'price':
                continue
            
            if alert.symbol != symbol:
                continue
            
            triggered = False
            
            if alert.condition == 'above' and current_price > alert.threshold:
                triggered = True
            elif alert.condition == 'below' and current_price < alert.threshold:
                triggered = True
            
            if triggered:
                self.trigger_alert(alert)
    
    def trigger_alert(self, alert: Alert):
        """Trigger an alert."""
        alert.triggered_at = datetime.now()
        alert.active = False
        self.save_alerts()
        
        logger.info(f"Alert triggered: {alert.message}")
        
        # Send notifications
        self.send_notification(alert)
    
    def send_notification(self, alert: Alert):
        """Send alert notification."""
        # In-app notification (log)
        logger.warning(f"[{alert.priority.upper()}] {alert.message}")
        
        # Could add email/Telegram here
        pass
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return [a for a in self.alerts if a.active]
    
    def delete_alert(self, alert_id: str):
        """Delete an alert."""
        self.alerts = [a for a in self.alerts if a.id != alert_id]
        self.save_alerts()


class EmailNotifier:
    """Send email notifications."""
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str,
                 password: str):
        """Initialize email notifier."""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_email(self, to: str, subject: str, body: str):
        """Send email notification."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


class TelegramNotifier:
    """Send Telegram notifications."""
    
    def __init__(self, bot_token: str, chat_id: str):
        """Initialize Telegram notifier."""
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    def send_message(self, message: str):
        """Send Telegram message."""
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {'chat_id': self.chat_id, 'text': message}
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logger.info("Telegram message sent")
                return True
            else:
                logger.error(f"Telegram error: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to send Telegram: {e}")
            return False


if __name__ == "__main__":
    manager = AlertManager()
    print(f"Loaded {len(manager.alerts)} alerts")
    
    # Test create alert
    alert = manager.create_alert(
        alert_type='price',
        priority='high',
        condition='above',
        message='BTC above $50,000',
        symbol='BTCUSDT',
        threshold=50000
    )
    print(f"Created alert: {alert.id}")
