# CIAF Demo - Quick Reference Card

## 🚀 Quick Start (30 seconds)

```bash
# Clone and navigate
cd d:\Github\agents

# Install dependencies
pip install -r requirements.txt

# Run locally
python run_local.py

# Open browser
# → http://localhost:5000
```

## 📋 Pre-Deployment Checklist

### Local Testing
- [ ] Run `python run_local.py` successfully
- [ ] Open http://localhost:5000 in browser
- [ ] See "System Online" status badge
- [ ] Select an agent (click card or dropdown)
- [ ] Execute "Read Data" action successfully
- [ ] Request privilege elevation
- [ ] Execute "Delete Data" with elevation
- [ ] View audit trail (shows entries)
- [ ] Check "Chain Status: ✓ Valid"
- [ ] Run `python examples.py` - all tests pass

### Code Review
- [ ] Review `api/index.py` - customize agents/roles if needed
- [ ] Check `requirements.txt` - ensure pyciaf version correct
- [ ] Verify `vercel.json` - configuration looks good
- [ ] Update `README.md` - add your repository URL
- [ ] Review `package.json` - update author/description

### Deployment
- [ ] Git repository initialized
- [ ] Code committed to Git
- [ ] Pushed to GitHub (optional but recommended)
- [ ] Vercel account created
- [ ] Vercel CLI installed OR plan to use dashboard
- [ ] Run deployment script OR manual deploy
- [ ] Deployment successful (got URL)
- [ ] Test deployed URL in browser
- [ ] All scenarios work on deployed version

### Post-Deployment
- [ ] Test all 5 scenarios on live site
- [ ] Check Vercel function logs (no errors)
- [ ] Verify mobile responsiveness
- [ ] Share demo URL with stakeholders
- [ ] Document any custom changes made
- [ ] Set up custom domain (optional)
- [ ] Enable Vercel analytics (optional)

## 🎯 5 Must-Try Scenarios

### 1. ✅ Successful Access (Same Tenant)
```
Agent: Analytics Agent Alpha
Action: Read Data
Resource: dataset-2026-q1
Tenant: acme-corp ✓ (matches agent)
Expected: SUCCESS
```

### 2. ❌ Tenant Isolation (Cross-Tenant)
```
Agent: Analytics Agent Alpha (acme-corp)
Action: Read Data  
Resource: secret-data
Tenant: techstart-inc ✗ (different!)
Expected: DENIED
```

### 3. ⚡ Privilege Elevation
```
Step 1: Try Delete Data → DENIED
Step 2: Request Elevation → GRANTED
Step 3: Retry Delete Data → SUCCESS
```

### 4. 📄 Export Report
```
Agent: Analytics Agent Beta
Action: Export Report
Resource: report-annual-2026
Tenant: techstart-inc
Expected: SUCCESS (PDF generated)
```

### 5. 📜 Audit Verification
```
Execute several actions
Click "Refresh Audit Trail"
Check: Chain Status = ✓ Valid
Verify: All actions logged
```

## 🔑 Key Concepts (30-Second Primer)

**CIAF** = Contextual Identity and Authorization Framework

**IAM** = Who can do what
- Agents have roles
- Roles have permissions
- Permissions have conditions

**PAM** = Temporary elevated access
- Time-bound grants (30 min)
- Requires approval reference
- Fully audited

**ABAC** = Attribute-based decisions
- `same_tenant_only` = most common
- Checks agent.tenant == resource.tenant

**Evidence Vault** = Tamper-proof audit
- Cryptographic signatures
- Chain verification
- Compliance ready

## 🌐 Deployment Commands

### Vercel CLI
```bash
npm install -g vercel
vercel login
vercel --prod
```

### Quick Deploy Script
```bash
# Unix/Mac
chmod +x deploy.sh && ./deploy.sh

# Windows  
deploy.bat
```

### Manual
1. Push code to GitHub
2. Go to vercel.com
3. "New Project" → Import repo
4. Deploy

## 🧪 Testing Commands

```bash
# Test locally
python run_local.py

# Run automated tests
python examples.py

# Test specific URL
python examples.py https://your-app.vercel.app

# API health check
curl http://localhost:5000/

# Initialize system
curl -X POST http://localhost:5000/api/init

# Get agents
curl http://localhost:5000/api/agents

# Execute action
curl -X POST http://localhost:5000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"agent-demo-001","action":"read_data","resource_id":"test","resource_tenant":"acme-corp"}'
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `api/index.py` | Backend API & CIAF logic |
| `public/index.html` | Web interface |
| `public/app.js` | Frontend logic |
| `public/styles.css` | Styling |
| `vercel.json` | Deployment config |
| `requirements.txt` | Python deps |
| `run_local.py` | Local dev server |
| `examples.py` | Test suite |
| `README.md` | Main docs |
| `DEPLOYMENT.md` | Deploy guide |
| `USER_GUIDE.md` | User manual |

## 🐛 Common Issues

### "Module not found: ciaf"
→ Check `requirements.txt` has `pyciaf==1.3.1`  
→ Or app runs in mock mode (expected for demo)

### "Connection refused"
→ Ensure server running: `python run_local.py`  
→ Check correct port (5000)

### "Action denied"
→ Verify resource tenant matches agent tenant  
→ Check if elevation needed (delete_data)

### "Chain invalid"
→ Shouldn't happen (indicates bug)  
→ Restart server and retry

## 💡 Customization Quick Wins

### Change Agent Name
`api/index.py` line ~70:
```python
display_name="Your Custom Name Here"
```

### Add New Tenant
`api/index.py` line ~80:
```python
tenant_id="your-company-name"
```

### Change Primary Color
`public/styles.css` line ~10:
```css
--primary-color: #your-hex-color;
```

### Add Custom Action
`api/index.py` line ~120:
```python
def your_tool(param: str):
    return {"status": "success"}
executor.register_tool("your_action", your_tool)
```

## 📊 Expected Performance

- **Local**: Instant (<50ms)
- **Vercel Cold Start**: 1-2 seconds
- **Vercel Warm**: <200ms
- **Page Load**: <500ms

## 🎓 Learning Path

1. **5 min**: Deploy and test locally
2. **10 min**: Try all 5 scenarios
3. **15 min**: Read USER_GUIDE.md
4. **30 min**: Explore code in api/index.py
5. **60 min**: Customize agents & roles
6. **90 min**: Deploy to Vercel
7. **120 min**: Add custom features

## 📞 Getting Help

1. Check DEPLOYMENT.md troubleshooting
2. Review Vercel function logs
3. Run local tests: `python examples.py`
4. Check browser console (F12)
5. Review this quick reference

## 🎉 Success Criteria

Your demo is working when:
- ✅ Status shows "System Online"
- ✅ Can select agents
- ✅ Same-tenant access works
- ✅ Cross-tenant access denied
- ✅ Elevation grants work
- ✅ Audit trail shows actions
- ✅ Chain status is Valid
- ✅ All examples.py tests pass

---

**TIP**: Bookmark this file for quick reference during demos! 🔖
