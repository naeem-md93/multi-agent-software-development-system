#!/bin/bash

# Navigate to the project directory
cd /home/naeem-md93/Projects/multi-agent-software-development-system/merchandise_template_generator

# Create or update the Python script with the validate_url function
cat <<EOL > validate_url.py
"""
validate_url.py

This script contains functionality to accept a URL as input and validate its format.
Unsupported schemes like 'ftp' are rejected.
"""

import validators

def validate_url(url):
    """
    Validates the given URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid and uses a supported scheme, False otherwise.
    """
    if not validators.url(url):
        return False

    # Check for unsupported schemes
    unsupported_schemes = ['ftp']
    scheme = url.split(':')[0].lower()
    if scheme in unsupported_schemes:
        return False

    return True

def main():
    """
    Main function to handle URL input and validation.
    """
    try:
        url = input("Enter a URL: ").strip()
        if not url:
            print("No URL provided. Please enter a valid URL.")
            return

        if validate_url(url):
            print("The URL is valid.")
        else:
            print("The URL is invalid or uses an unsupported scheme.")
    except EOFError:
        print("Input ended unexpectedly. Please try again.")

if __name__ == "__main__":
    main()
EOL

# Print a message indicating the script has been created or updated
echo "validate_url.py script has been created/updated successfully."
