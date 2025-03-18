#!/bin/bash

# Fix Django import resolution issues
echo "Fixing Django import resolution issues..."

# Ensure Django is installed in the active environment
cd docautomation_backend
source venv/bin/activate || (python3 -m venv venv && source venv/bin/activate)
pip install -r requirements.txt

# Create VSCode settings if needed
mkdir -p ../.vscode
cat > ../.vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "${PWD}/venv/bin/python",
    "python.analysis.extraPaths": ["${PWD}"],
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.pylintArgs": [
        "--load-plugins=pylint_django",
        "--django-settings-module=docautomation_backend.settings"
    ]
}
EOF

echo "Created VSCode settings with proper Python path"
echo "If using PyCharm, mark the directory as a Django project in settings"
echo "You may need to restart your editor for changes to take effect" 