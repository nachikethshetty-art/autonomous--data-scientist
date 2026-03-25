"""
Module 14: Automated Alerting System
Send alerts via multiple channels (Slack, Email, SMS).
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"
    OK = "OK"


class AlertChannel(Enum):
    """Alert delivery channels."""
    SLACK = "slack"
    EMAIL = "email"
    SMS = "sms"
    LOG = "log"
    WEBHOOK = "webhook"


@dataclass
class Alert:
    """Alert data structure."""
    job_id: str
    title: str
    message: str
    severity: AlertSeverity
    category: str  # drift, performance, retraining, etc.
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    channels: List[AlertChannel] = field(default_factory=list)
    resolved: bool = False


class AlertManager:
    """
    Comprehensive alerting system.
    
    Features:
    - Multi-channel alert delivery
    - Alert routing based on severity
    - Alert deduplication
    - Alert history tracking
    - Configurable thresholds
    - Smart escalation
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize alert manager.
        
        Args:
            config_file: Path to alerting configuration
        """
        self.alerts_dir = Path("data/alerts")
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
        
        self.alert_history = {}
        self.config = self._load_config(config_file)
        self.channels = self._initialize_channels()
    
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """Load alerting configuration."""
        default_config = {
            'slack': {
                'enabled': False,
                'webhook_url': None,
                'channel': '#alerts'
            },
            'email': {
                'enabled': False,
                'recipients': [],
                'smtp_server': None,
                'from_address': None
            },
            'sms': {
                'enabled': False,
                'recipients': [],
                'api_key': None
            },
            'escalation': {
                'critical_recipients': [],
                'warning_recipients': [],
                'retry_count': 3,
                'retry_delay': 60
            }
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")
        
        return default_config
    
    def _initialize_channels(self) -> Dict:
        """Initialize alert channels."""
        channels = {}
        
        # Log channel (always available)
        channels['log'] = self._create_log_channel()
        
        # Slack channel
        if self.config['slack']['enabled']:
            channels['slack'] = self._create_slack_channel()
        
        # Email channel
        if self.config['email']['enabled']:
            channels['email'] = self._create_email_channel()
        
        # SMS channel
        if self.config['sms']['enabled']:
            channels['sms'] = self._create_sms_channel()
        
        return channels
    
    def _create_log_channel(self):
        """Create logging channel."""
        return {
            'type': 'log',
            'send': lambda alert: self._send_log_alert(alert)
        }
    
    def _create_slack_channel(self):
        """Create Slack channel (stub for integration)."""
        return {
            'type': 'slack',
            'send': lambda alert: self._send_slack_alert(alert)
        }
    
    def _create_email_channel(self):
        """Create Email channel (stub for integration)."""
        return {
            'type': 'email',
            'send': lambda alert: self._send_email_alert(alert)
        }
    
    def _create_sms_channel(self):
        """Create SMS channel (stub for integration)."""
        return {
            'type': 'sms',
            'send': lambda alert: self._send_sms_alert(alert)
        }
    
    def send_alert(self, job_id: str, title: str, message: str,
                  severity: AlertSeverity, category: str,
                  metadata: Optional[Dict] = None,
                  channels: Optional[List[AlertChannel]] = None) -> Dict:
        """
        Send alert through configured channels.
        
        Args:
            job_id: Job identifier
            title: Alert title
            message: Alert message
            severity: Alert severity level
            category: Alert category
            metadata: Additional metadata
            channels: Specific channels to use
        
        Returns:
            Alert delivery report
        """
        alert = Alert(
            job_id=job_id,
            title=title,
            message=message,
            severity=severity,
            category=category,
            metadata=metadata or {},
            channels=channels or self._get_default_channels(severity)
        )
        
        # Check for duplicate alerts
        if self._is_duplicate(alert):
            logger.info(f"Duplicate alert suppressed: {title}")
            return {'status': 'suppressed', 'reason': 'duplicate'}
        
        # Send through configured channels
        results = {}
        for channel in alert.channels:
            try:
                if channel.value in self.channels:
                    self.channels[channel.value]['send'](alert)
                    results[channel.value] = 'sent'
                else:
                    results[channel.value] = 'channel_not_configured'
            except Exception as e:
                logger.error(f"Failed to send via {channel.value}: {e}")
                results[channel.value] = f'error: {str(e)}'
        
        # Store in history
        self._store_alert(alert)
        
        return {
            'alert_id': f"{job_id}_{alert.timestamp.timestamp()}",
            'status': 'sent',
            'channels': results,
            'timestamp': alert.timestamp.isoformat()
        }
    
    def _get_default_channels(self, severity: AlertSeverity) -> List[AlertChannel]:
        """Get default channels based on severity."""
        channels = [AlertChannel.LOG]
        
        if severity == AlertSeverity.CRITICAL:
            if self.config['slack']['enabled']:
                channels.append(AlertChannel.SLACK)
            if self.config['email']['enabled']:
                channels.append(AlertChannel.EMAIL)
            if self.config['sms']['enabled']:
                channels.append(AlertChannel.SMS)
        elif severity == AlertSeverity.WARNING:
            if self.config['slack']['enabled']:
                channels.append(AlertChannel.SLACK)
            if self.config['email']['enabled']:
                channels.append(AlertChannel.EMAIL)
        
        return channels
    
    def _is_duplicate(self, alert: Alert) -> bool:
        """Check if alert is duplicate (within last hour)."""
        key = f"{alert.job_id}_{alert.category}"
        
        if key in self.alert_history:
            last_alert = self.alert_history[key]
            # Suppress duplicate within 1 hour
            time_diff = (alert.timestamp - last_alert['timestamp']).total_seconds()
            if time_diff < 3600:
                return True
        
        return False
    
    def _store_alert(self, alert: Alert):
        """Store alert in history and disk."""
        key = f"{alert.job_id}_{alert.category}"
        self.alert_history[key] = {
            'timestamp': alert.timestamp,
            'severity': alert.severity.value
        }
        
        # Save to disk
        alert_file = self.alerts_dir / f"{alert.job_id}_alerts.jsonl"
        with open(alert_file, 'a') as f:
            f.write(json.dumps({
                'timestamp': alert.timestamp.isoformat(),
                'title': alert.title,
                'message': alert.message,
                'severity': alert.severity.value,
                'category': alert.category,
                'metadata': alert.metadata
            }) + '\n')
    
    def _send_log_alert(self, alert: Alert):
        """Send alert to logs."""
        log_level = {
            AlertSeverity.CRITICAL: logging.CRITICAL,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.OK: logging.INFO
        }.get(alert.severity, logging.INFO)
        
        logger.log(log_level, f"[{alert.severity.value}] {alert.title}: {alert.message}")
    
    def _send_slack_alert(self, alert: Alert):
        """Send alert to Slack (stub)."""
        logger.info(f"[SLACK] {alert.title}: {alert.message}")
        # Implementation would use Slack SDK
    
    def _send_email_alert(self, alert: Alert):
        """Send alert via Email (stub)."""
        logger.info(f"[EMAIL] {alert.title}: {alert.message}")
        # Implementation would use SMTP
    
    def _send_sms_alert(self, alert: Alert):
        """Send alert via SMS (stub)."""
        logger.info(f"[SMS] {alert.title}: {alert.message}")
        # Implementation would use SMS API
    
    def get_alert_history(self, job_id: str) -> List[Dict]:
        """Get alert history for a job."""
        alert_file = self.alerts_dir / f"{job_id}_alerts.jsonl"
        
        if not alert_file.exists():
            return []
        
        alerts = []
        with open(alert_file, 'r') as f:
            for line in f:
                try:
                    alerts.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return alerts
    
    def resolve_alert(self, job_id: str, category: str) -> Dict:
        """Resolve/clear an alert."""
        key = f"{job_id}_{category}"
        if key in self.alert_history:
            del self.alert_history[key]
        
        return {'status': 'resolved', 'job_id': job_id, 'category': category}
