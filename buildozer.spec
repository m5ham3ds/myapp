[app]

# (str) Title of your application
title = Shadow

# (str) Package name
package.name = Shadow

# (str) Package domain (unique identifier)
package.domain = org.example

# (str) Source code where the main.py is located
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 1.0

# (list) Application dependencies
# Ensure all necessary Python packages are included here
requirements = python3,kivy,requests,pillow,beautifulsoup4,git,moviepy

# (list) Permissions
# Include all the necessary permissions your app needs
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, SYSTEM_ALERT_WINDOW, WAKE_LOCK

# (str) Presplash of the application
# Path to the presplash image shown while the app is loading
presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# Path to the app icon
icon.filename = %(source.dir)s/logo.png

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (list) Supported android API (minimum supported version)
android.api = 27

# (str) Android NDK version to use
android.ndk = 21b

# (bool) Enable Android logcat
android.logcat = 1

# (str) Android logcat filters
android.logcat.filters = *:S python:D

# (bool) Copy the .pyo/.pyc files into the final APK
android.keep_pyo = 1

# (str) Path to your keystore
# Required for signing your app for release. Update this path to your keystore file
android.release.keystore = /path/to/your/keystore

# (str) Keystore password
android.release.keystore_passwd = your-keystore-password

# (str) Key alias
android.release.keyalias = your-keyalias

# (str) Key password
android.release.keyalias_passwd = your-keyalias-password