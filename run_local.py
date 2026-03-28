"""
Local Development Server for CIAF Demo
Run this file to test locally before deploying to Vercel
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api.index import app
except ImportError as e:
    print(f"Error importing Flask app: {e}")
    print("\nMake sure you've installed the requirements:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║  CIAF Agentic Workflow Demo - Development Server    ║
    ╚══════════════════════════════════════════════════════╝
    
    🚀 Server starting on: http://localhost:{port}
    
    📚 Features:
       - Interactive agent execution
       - Multi-tenant isolation demo
       - Privilege elevation workflows
       - Cryptographic audit trail
    
    Press Ctrl+C to stop the server
    """)

    app.run(host="0.0.0.0", port=port, debug=True)
