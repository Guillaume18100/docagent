#!/usr/bin/env python3
"""
Fix settings.py file for Django project
"""
import os
import sys

def fix_django_settings():
    # Get the settings file path
    settings_file = os.path.join('docautomation_backend', 'docautomation_backend', 'settings.py')
    
    if not os.path.exists(settings_file):
        print(f"Error: Settings file not found at {settings_file}")
        return False
    
    # Read the settings file
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Check if 'import os' is already in the file
    if 'import os' not in content:
        print("Adding 'import os' to settings.py...")
        content = 'import os\n' + content
        
        # Write the modified content back to the file
        with open(settings_file, 'w') as f:
            f.write(content)
        
        print("Added 'import os' to settings.py")
    else:
        print("'import os' already exists in settings.py")
    
    # Check for other necessary settings
    required_settings = {
        "rest_framework": "'rest_framework'",
        "corsheaders": "'corsheaders'",
        "document_processing": "'document_processing'",
        "nlp": "'nlp'",
        "document_generation": "'document_generation'",
    }
    
    # Check which settings are missing
    missing_settings = []
    for key, value in required_settings.items():
        if value not in content:
            missing_settings.append(value)
    
    if missing_settings:
        print(f"Adding missing apps to INSTALLED_APPS: {', '.join(missing_settings)}")
        
        # Find the INSTALLED_APPS list and add the missing settings
        if "INSTALLED_APPS = [" in content:
            parts = content.split("INSTALLED_APPS = [")
            apps_part = parts[1].split("]")[0]
            
            # Add the missing settings
            new_apps = apps_part
            if missing_settings:
                if not new_apps.endswith(',\n'):
                    new_apps += ','
                new_apps += "\n    # Third-party apps\n"
                if "'rest_framework'" in missing_settings:
                    new_apps += "    'rest_framework',\n"
                if "'corsheaders'" in missing_settings:
                    new_apps += "    'corsheaders',\n"
                new_apps += "\n    # Project apps\n"
                if "'document_processing'" in missing_settings:
                    new_apps += "    'document_processing',\n"
                if "'nlp'" in missing_settings:
                    new_apps += "    'nlp',\n"
                if "'document_generation'" in missing_settings:
                    new_apps += "    'document_generation',\n"
            
            # Reconstruct the content
            new_content = parts[0] + "INSTALLED_APPS = [" + new_apps + "]" + parts[1].split("]", 1)[1]
            
            # Write the modified content back to the file
            with open(settings_file, 'w') as f:
                f.write(new_content)
            
            print("Added missing apps to INSTALLED_APPS")
    else:
        print("All required apps are already in INSTALLED_APPS")
    
    # Add CORS and media settings if missing
    additional_settings = """
# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Media files (Uploaded documents)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}
"""
    
    if "CORS_ALLOW_ALL_ORIGINS" not in content:
        print("Adding CORS and media settings...")
        
        # Append the additional settings to the end of the file
        with open(settings_file, 'a') as f:
            f.write(additional_settings)
        
        print("Added CORS and media settings")
    else:
        print("CORS and media settings already exist")
    
    return True

if __name__ == "__main__":
    print("Running Django settings fixer...")
    success = fix_django_settings()
    if success:
        print("Settings fixed successfully.")
    else:
        print("Failed to fix settings.")
        sys.exit(1) 