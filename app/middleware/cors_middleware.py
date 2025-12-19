from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    """
    Setup CORS middleware untuk aplikasi

    Note: Untuk production, ganti allow_origins dengan domain spesifik
    Example: allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"]
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Untuk production, ganti dengan domain spesifik
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
