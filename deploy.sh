#!/bin/bash

# CIAF Demo - Quick Deployment Script
# This script helps you deploy the demo to Vercel quickly

set -e

echo "╔══════════════════════════════════════════════════════╗"
echo "║   CIAF Agentic Workflow - Quick Deploy Script       ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: CIAF Agentic Workflow Demo"
    echo "✓ Git repository initialized"
    echo ""
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "⚠️  Vercel CLI not found"
    echo "Would you like to install it? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "📦 Installing Vercel CLI..."
        npm install -g vercel
        echo "✓ Vercel CLI installed"
    else
        echo ""
        echo "ℹ️  You can install Vercel CLI later with:"
        echo "   npm install -g vercel"
        echo ""
        echo "Or deploy via Vercel Dashboard:"
        echo "   1. Push code to GitHub"
        echo "   2. Go to vercel.com"
        echo "   3. Import your repository"
        echo ""
        exit 0
    fi
fi

echo ""
echo "🚀 Deploying to Vercel..."
echo ""

# Login to Vercel (if not already)
vercel login

# Deploy
echo ""
echo "Deploying project..."
vercel --prod

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║              🎉 Deployment Complete! 🎉             ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "Your CIAF demo is now live!"
echo ""
echo "Next steps:"
echo "  1. Open the URL provided above"
echo "  2. Select an agent and try executing actions"
echo "  3. Test privilege elevation"
echo "  4. View the audit trail"
echo ""
echo "📖 Documentation:"
echo "   - User Guide: USER_GUIDE.md"
echo "   - Deployment Guide: DEPLOYMENT.md"
echo "   - README: README.md"
echo ""
echo "Need help? Check DEPLOYMENT.md for troubleshooting."
echo ""
