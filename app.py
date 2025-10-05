# Root-level FastAPI entrypoint for Vercel deployment
from api.index import app

# This file serves as the entrypoint that Vercel expects
# It imports the FastAPI app from the api/index.py module
