# Importar todos los modelos para que SQLAlchemy los reconozca
from .user import User, base
from .campaign import Campaign
from .metric import Metric
from .feedback import Feedback

# Exportar todo para facilitar las importaciones
__all__ = ["User", "Campaign", "Metric", "Feedback", "base"]
