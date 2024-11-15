import uuid

def generate_secure_url(filename):
    # Generate a secure URL for file download
    return f"/download-file/{uuid.uuid4()}_{filename}"