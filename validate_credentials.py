import json
import os

def validate_firebase_credentials(cred_json):
    try:
        # Try to parse the JSON
        cred_dict = json.loads(cred_json)

        # Required fields for Firebase Admin SDK
        required_fields = [
            'type',
            'project_id',
            'private_key_id',
            'private_key',
            'client_email',
            'client_id',
            'auth_uri',
            'token_uri',
            'auth_provider_x509_cert_url',
            'client_x509_cert_url'
        ]

        # Check for required fields
        missing_fields = [field for field in required_fields if field not in cred_dict]

        if missing_fields:
            print(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False

        # Check credential type
        if cred_dict['type'] != 'service_account':
            print("❌ Invalid credential type. Must be 'service_account'")
            return False

        # Check private key format
        if 'private_key' in cred_dict:
            private_key = cred_dict['private_key'].replace('\\n', '\n')
            if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
                print("❌ Invalid private key format")
                return False

        print("✅ Credentials format is valid!")
        print(f"Project ID: {cred_dict['project_id']}")
        print(f"Client Email: {cred_dict['client_email']}")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {str(e)}")
        return False

# Get credentials from environment variable
credentials = os.environ.get('FIREBASE_CREDENTIALS')
if not credentials:
    print("❌ FIREBASE_CREDENTIALS environment variable not found")
else:
    validate_firebase_credentials(credentials)