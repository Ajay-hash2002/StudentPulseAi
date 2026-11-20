try:
    from mangum import Mangum
    from app.main import app
    handler = Mangum(app)
except ImportError:
    # If mangum is not yet installed in local environment
    handler = None
