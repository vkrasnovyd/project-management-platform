import os


# Include the environment-specific settings file based on the environment
if os.environ.get("ENV_NAME") == "DEVELOPMENT":
    from .development import *
elif os.environ.get("ENV_NAME") == "PRODUCTION":
    from .production import *
