import json

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
            'client_email'
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

# Example usage
print("Paste your Firebase credentials JSON and press Enter twice:")
lines = []
while True:
    line = input()
    if line:
        lines.append(line)
    else:
        break
credentials = '\n'.join(lines)

validate_firebase_credentials(credentials)
