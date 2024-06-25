import os

from split_settings.tools import include

# Include the base settings file
include("base.py")

# Include the environment-specific settings file based on the environment
if os.environ.get("ENV_NAME") == "DEVELOPMENT":
    include("development.py")
elif os.environ.get("ENV_NAME") == "PRODUCTION":
    include("production.py")
