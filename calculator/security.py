import os
import hashlib
import hmac
import base64

# Secret key for HMAC (loaded from environment variable for security)
SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')

def generate_api_key(user_id):
    """Generate a unique API key for a given user using HMAC."""
    message = user_id.encode('utf-8')
    secret = SECRET_KEY.encode('utf-8')
    signature = hmac.new(secret, message, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode('utf-8')

def validate_api_key(user_id, api_key):
    """Validate the provided API key by regenerating it and comparing."""
    expected_key = generate_api_key(user_id)
    return hmac.compare_digest(expected_key, api_key)

if __name__ == '__main__':
    # Example usage
    user_id = 'user123'
    api_key = generate_api_key(user_id)
    print(f'Generated API key: {api_key}')
    is_valid = validate_api_key(user_id, api_key)
    print(f'Is API key valid? {is_valid}')
