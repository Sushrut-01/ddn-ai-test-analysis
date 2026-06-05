import os
uri = os.getenv('MONGODB_URI', '')
print(f"URI length: {len(uri)}")
print(f"Has %40: {'%40' in uri}")
print(f"@ count: {uri.count('@')}")
if '//' in uri and '@' in uri:
    parts = uri.split('//')
    if len(parts) > 1:
        creds = parts[1].split('@')[0]
        print(f"Credentials: {creds}")
        if ':' in creds:
            password = creds.split(':')[1]
            print(f"Password: {password}")
