class SensorMetricsError(Exception):
    pass


class SensorNotFoundError(SensorMetricsError):
    pass


class DatabaseError(SensorMetricsError):
    pass


class ValidationError(SensorMetricsError):
    pass
