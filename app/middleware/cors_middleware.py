from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    """
    Setup CORS middleware for the application

    Note: For production, replace allow_origins with specific domains
    Example: allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"]
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For production, replace with specific domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
