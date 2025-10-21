"""
Custom exceptions for the sensor metrics system.
"""


class SensorMetricsError(Exception):
    """Base exception for sensor metrics system."""

    pass


class SensorNotFoundError(SensorMetricsError):
    """Raised when a sensor is not found."""

    pass


class DatabaseError(SensorMetricsError):
    """Raised when database operation fails."""

    pass


class ValidationError(SensorMetricsError):
    """Raised when data validation fails."""

    pass


class ConfigurationError(SensorMetricsError):
    """Raised when configuration is invalid."""

    pass
