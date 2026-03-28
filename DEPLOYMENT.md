# CIAF Demo - Deployment Guide

## 🚀 Deploying to Vercel

This guide will walk you through deploying your CIAF Agentic Workflow demo to Vercel.

### Prerequisites

- GitHub account
- Vercel account (free tier works great!)
- Git installed locally

### Step 1: Prepare Your Repository

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: CIAF Agentic Workflow Demo"

# Create GitHub repository and push
# (Follow GitHub's instructions for creating a new repository)
git remote add origin https://github.com/yourusername/ciaf-demo.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Vercel

#### Option A: Vercel Dashboard (Easiest)

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the configuration from `vercel.json`
5. Click "Deploy"
6. Wait 1-2 minutes for deployment to complete
7. Your app is live! 🎉

#### Option B: Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy (first time)
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? [your account]
# - Link to existing project? No
# - What's your project's name? ciaf-demo
# - In which directory is your code located? ./
# - Want to override settings? No

# Deploy to production
vercel --prod
```

### Step 3: Verify Deployment

After deployment, Vercel will give you a URL like:
```
https://ciaf-demo-xxxx.vercel.app
```

Test your deployment:

1. **Open the URL** in your browser
2. **Check status badge** - should show "System Online"
3. **Select an agent** from the agents section
4. **Execute an action** - try "Read Data"
5. **View audit trail** - verify actions are logged

### Step 4: Custom Domain (Optional)

1. In Vercel dashboard, go to your project
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions
5. Wait for DNS propagation (5-60 minutes)

## 🔧 Configuration

### Environment Variables

For production deployments, you can add environment variables in Vercel:

1. Go to Project Settings → Environment Variables
2. Add variables:

```
SIGNING_SECRET=your-super-secret-key-here
COMPLIANCE_FRAMEWORKS=HIPAA,GDPR,SOX
FLASK_ENV=production
```

3. Redeploy for changes to take effect

### Custom Configuration

Edit `api/index.py` to customize:

- Agents and their tenants
- Roles and permissions  
- Sensitive actions requiring elevation
- Compliance frameworks
- Business logic

Then commit and push:

```bash
git add api/index.py
git commit -m "Update configuration"
git push
```

Vercel will automatically redeploy!

## 🧪 Testing Your Deployment

### Manual Testing

Use these scenarios to verify functionality:

#### Test 1: Successful Authorization
- Agent: Analytics Agent Alpha (acme-corp)
- Action: Read Data
- Resource ID: dataset-2026-q1
- Resource Tenant: acme-corp
- Expected: ✓ Success

#### Test 2: Multi-Tenant Isolation
- Agent: Analytics Agent Alpha (acme-corp)
- Action: Read Data
- Resource ID: dataset-sensitive
- Resource Tenant: techstart-inc
- Expected: ✗ Denied (Tenant mismatch)

#### Test 3: Privilege Elevation
1. Select Analytics Agent Alpha
2. Click "Request Privilege Elevation"
3. Try "Delete Data" action
4. Expected: ✓ Success (with valid grant)

#### Test 4: Audit Trail
1. Execute several actions
2. Click "Refresh Audit Trail"
3. Verify all actions logged
4. Check "Chain Status: ✓ Valid"

### API Testing

Use curl or Postman:

```bash
# Test initialization
curl -X POST https://your-app.vercel.app/api/init

# Get agents
curl https://your-app.vercel.app/api/agents

# Execute action
curl -X POST https://your-app.vercel.app/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent-demo-001",
    "action": "read_data",
    "resource_id": "dataset-test",
    "resource_tenant": "acme-corp",
    "justification": "API test"
  }'

# Get audit trail
curl https://your-app.vercel.app/api/audit
```

## 🐛 Troubleshooting

### Build Failures

**Problem**: Vercel build fails with "Module not found: ciaf"

**Solution**: 
- CIAF needs to be installable via pip
- If using a local/private package, add to `requirements.txt` as Git URL:
  ```
  git+https://github.com/yourusername/ciaf.git@v1.3.1#egg=pyciaf
  ```
- Or use the published PyPI package:
  ```
  pyciaf==1.3.1
  ```

**Problem**: Build succeeds but app doesn't work

**Solution**:
- Check Vercel Logs in the dashboard
- Ensure `vercel.json` routing is correct
- Verify Python version compatibility (3.9+)

### Runtime Errors

**Problem**: "500 Internal Server Error" when calling API

**Solution**:
- Check Function Logs in Vercel dashboard
- Look for Python import errors
- Verify all dependencies in requirements.txt
- Test locally first: `python run_local.py`

**Problem**: "CIAF not available" warning

**Solution**:
- This is expected if CIAF can't be imported
- App will run in mock mode for demo purposes
- Install real CIAF package for full functionality

### Performance Issues

**Problem**: API calls are slow

**Solution**:
- Vercel cold starts can take 1-2 seconds
- Consider upgrading to Pro for better performance
- Implement caching for frequently accessed data
- Use Vercel Edge Functions for critical paths

## 📊 Monitoring

### Vercel Analytics

Enable analytics in Project Settings:
1. Go to "Analytics" tab
2. Enable Web Analytics
3. View real-time usage data

### Custom Logging

Add logging to `api/index.py`:

```python
import logging
logging.basicConfig(level=logging.INFO)

@app.route('/api/execute', methods=['POST'])
def execute_action():
    logging.info(f"Execution request: {request.get_json()}")
    # ... rest of code
```

View logs in Vercel Dashboard → Functions → View Logs

## 🔒 Security Hardening

For production deployments:

### 1. Add Authentication

```python
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not verify_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/execute', methods=['POST'])
@require_auth
def execute_action():
    # ... existing code
```

### 2. Add Rate Limiting

Use Vercel's rate limiting or add custom middleware:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/api/execute', methods=['POST'])
@limiter.limit("10 per minute")
def execute_action():
    # ... existing code
```

### 3. Use Environment Variables

Never hardcode secrets:

```python
import os

vault = EvidenceVault(
    signing_secret=os.environ.get('SIGNING_SECRET', 'demo-secret-key')
)
```

### 4. Enable CORS Properly

```python
CORS(app, origins=[
    'https://yourdomain.com',
    'https://*.vercel.app'
])
```

## 🎯 Next Steps

1. **Customize the UI**: Edit `public/styles.css` for branding
2. **Add More Scenarios**: Create additional agents and permissions
3. **Integrate with Real Systems**: Connect to actual data sources
4. **Add Persistence**: Use databases instead of in-memory storage
5. **Enable Analytics**: Track usage and performance
6. **Add Tests**: Implement automated testing

## 📞 Getting Help

- **Vercel Discord**: [vercel.com/discord](https://vercel.com/discord)
- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **CIAF Issues**: [github.com/yourorg/ciaf/issues](https://github.com/yourorg/ciaf/issues)

---

Happy deploying! 🚀
