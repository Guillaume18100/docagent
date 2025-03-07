#!/bin/bash

echo "==== Django Settings Fixer ===="
echo "This script will fix Django settings regardless of where the settings.py file is located"

# Find the settings.py file
echo "Searching for settings.py..."
settings_file=$(find . -name "settings.py" | head -n 1)

if [ -z "$settings_file" ]; then
    echo "ERROR: Could not find settings.py file"
    exit 1
fi

echo "Found settings.py at: $settings_file"

# Check if 'import os' is already in the file
if ! grep -q "import os" "$settings_file"; then
    echo "Adding 'import os' to settings.py..."
    # Create a temporary file
    temp_file="${settings_file}.temp"
    echo "import os" > "$temp_file"
    cat "$settings_file" >> "$temp_file"
    mv "$temp_file" "$settings_file"
    echo "Added 'import os' to settings.py"
else
    echo "'import os' already exists in settings.py"
fi

# Check for installed apps
if ! grep -q "'document_processing'" "$settings_file"; then
    echo "Adding required apps to INSTALLED_APPS..."
    # Find the INSTALLED_APPS section and modify it
    awk '
    /INSTALLED_APPS = \[/ {
        print $0;
        print "    # Third-party apps";
        print "    '\''rest_framework'\'',";
        print "    '\''corsheaders'\'',";
        print "";
        print "    # Project apps";
        print "    '\''document_processing'\'',";
        print "    '\''nlp'\'',";
        print "    '\''document_generation'\'',";
        in_apps = 1;
        next;
    }
    in_apps == 1 && /\]/ {
        in_apps = 0;
    }
    { print $0 }
    ' "$settings_file" > "${settings_file}.temp"
    
    mv "${settings_file}.temp" "$settings_file"
    echo "Added required apps to INSTALLED_APPS"
else
    echo "Apps are already in INSTALLED_APPS"
fi

# Add CORS and media settings if not present
if ! grep -q "CORS_ALLOW_ALL_ORIGINS" "$settings_file"; then
    echo "Adding CORS and media settings..."
    cat >> "$settings_file" << EOF

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
EOF
    echo "Added CORS and media settings"
else
    echo "CORS and media settings already exist"
fi

echo "Settings fixed successfully!"
echo "Now try running: ./start.sh" 