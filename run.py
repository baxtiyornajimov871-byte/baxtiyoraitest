"""
BaxtiyorAiTest - Render.com uchun maxsus Entry Point
"""

import os
import sys

# Muhim: Render.com uchun pathni to'g'rilash
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app import create_app
    print("✅ Successfully imported create_app from app")
except ImportError as e:
    print("❌ Import error:", e)
    print("Current directory:", os.listdir('.'))
    print("App directory content:", os.listdir('app') if os.path.exists('app') else "No app folder")
    raise

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)