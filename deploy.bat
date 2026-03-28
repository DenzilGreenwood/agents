@echo off
REM CIAF Demo - Quick Deployment Script for Windows
REM This script helps you deploy the demo to Vercel quickly

echo ╔══════════════════════════════════════════════════════╗
echo ║   CIAF Agentic Workflow - Quick Deploy Script       ║
echo ╚══════════════════════════════════════════════════════╝
echo.

REM Check if git is initialized
if not exist ".git" (
    echo 📦 Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit: CIAF Agentic Workflow Demo"
    echo ✓ Git repository initialized
    echo.
)

REM Check if Vercel CLI is installed
where vercel >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Vercel CLI not found
    echo.
    echo Installing Vercel CLI...
    npm install -g vercel
    if %errorlevel% equ 0 (
        echo ✓ Vercel CLI installed
    ) else (
        echo ✗ Failed to install Vercel CLI
        echo.
        echo Please install manually:
        echo    npm install -g vercel
        echo.
        echo Or deploy via Vercel Dashboard:
        echo    1. Push code to GitHub
        echo    2. Go to vercel.com
        echo    3. Import your repository
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Deploying to Vercel...
echo.

REM Login to Vercel (if not already)
call vercel login

REM Deploy
echo.
echo Deploying project...
call vercel --prod

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║              🎉 Deployment Complete! 🎉             ║
echo ╚══════════════════════════════════════════════════════╝
echo.
echo Your CIAF demo is now live!
echo.
echo Next steps:
echo   1. Open the URL provided above
echo   2. Select an agent and try executing actions
echo   3. Test privilege elevation
echo   4. View the audit trail
echo.
echo 📖 Documentation:
echo    - User Guide: USER_GUIDE.md
echo    - Deployment Guide: DEPLOYMENT.md
echo    - README: README.md
echo.
echo Need help? Check DEPLOYMENT.md for troubleshooting.
echo.
pause
