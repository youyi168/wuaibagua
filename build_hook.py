# -*- coding: utf-8 -*-
"""
PyInstaller runtime hook for Kivy apps.
This prevents Kivy from initializing OpenGL during the build process.
"""
import os
import sys

# Set environment variables before Kivy imports
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '1'

# For CI/CD environments without GPU
if 'CI' in os.environ or 'GITHUB_ACTIONS' in os.environ:
    os.environ['KIVY_LOG_MODE'] = 'PYTHON'
