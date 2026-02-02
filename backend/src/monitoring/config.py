"""
Monitoring configuration for Customer Success Digital FTE.
"""

from typing import Optional
from pydantic import Field
from .config import Settings


class MonitoringSettings(Settings):
    """Monitoring-specific settings."""
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_STRUCTURED: bool = Field(default=True, description="Enable structured logging")
    LOG_INCLUDE_TRACEBACKS: bool = Field(default=True, description="Include tracebacks in logs")
    
    # Metrics settings
    METRICS_ENABLED: bool = Field(default=True, description="Enable metrics collection")
    METRICS_PREFIX: str = Field(default="fte", description="Prefix for all metrics")
    
    # Monitoring endpoints
    MONITORING_ENABLED: bool = Field(default=True, description="Enable monitoring endpoints")
    METRICS_ENDPOINT_ENABLED: bool = Field(default=True, description="Enable /metrics endpoint")
    
    # Alerting settings
    ALERT_ON_ERROR_RATE_THRESHOLD: float = Field(default=0.05, description="Error rate threshold for alerts")
    ALERT_ON_RESPONSE_TIME_THRESHOLD: float = Field(default=5.0, description="Response time threshold (seconds)")
    ALERT_ON_HIGH_CPU_USAGE: float = Field(default=80.0, description="CPU usage threshold for alerts (%)")
    ALERT_ON_LOW_MEMORY_AVAILABLE: float = Field(default=10.0, description="Low memory threshold (%)")
    
    # Tracing settings
    TRACING_ENABLED: bool = Field(default=False, description="Enable distributed tracing")
    TRACING_SAMPLING_RATE: float = Field(default=0.1, description="Tracing sampling rate")
    
    # Business metrics
    BUSINESS_METRICS_ENABLED: bool = Field(default=True, description="Enable business metrics collection")
    CUSTOMER_SATISFACTION_TRACKING: bool = Field(default=True, description="Track customer satisfaction")
    ESCALATION_METRICS_ENABLED: bool = Field(default=True, description="Track escalation metrics")
    
    class Config:
        env_file = ".env"
        env_prefix = "MONITORING_"


def get_monitoring_settings() -> MonitoringSettings:
    """Get monitoring settings instance."""
    return MonitoringSettings()