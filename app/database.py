from app.api.models.sensor_models import SensorCreateResponse

# In-memory storage for demo purposes
sensors_db: list[SensorCreateResponse] = []
metrics_db: list[dict] = []
