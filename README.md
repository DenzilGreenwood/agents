# CIAF Agentic Workflow Demo

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/ciaf-demo)

An interactive web demonstration of CIAF (Contextual Identity and Authorization Framework) v1.3.1 showcasing agentic execution boundaries with enterprise-grade security controls.

## 🌟 Features

- **Identity & Access Management (IAM)**: Role-based access control with attribute-based conditions
- **Multi-Tenant Isolation**: Automatic tenant boundary enforcement
- **Privilege Access Management (PAM)**: Time-bound privilege elevation for sensitive operations
- **Evidence Vault**: Cryptographically signed audit trail with chain-of-custody verification
- **Compliance Framework**: Built-in HIPAA, GDPR, and SOX obligation tracking
- **Interactive UI**: Live demonstration of all CIAF capabilities

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd agents
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the development server**
```bash
python run_local.py
```

4. **Open your browser**
```
http://localhost:5000
```

### Deploy to Vercel

#### Option 1: One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/ciaf-demo)

#### Option 2: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel
```

#### Option 3: GitHub Integration

1. Push your code to GitHub
2. Import project in Vercel dashboard
3. Vercel will auto-detect configuration
4. Deploy!

## 📁 Project Structure

```
agents/
├── api/
│   └── index.py          # Flask serverless function
├── public/
│   ├── index.html        # Main webpage
│   ├── styles.css        # Styling
│   └── app.js            # Frontend logic
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
├── run_local.py         # Local development server
└── README.md            # This file
```

## 🎯 Using the Demo

### 1. Select an Agent
Choose from pre-configured agents representing different tenants:
- **Analytics Agent Alpha** (acme-corp tenant)
- **Analytics Agent Beta** (techstart-inc tenant)

### 2. Execute Actions
Try different actions to see CIAF authorization in action:
- **Read Data**: Read datasets (requires `data_analyst` role)
- **Export Report**: Generate reports (requires `data_analyst` role)
- **Delete Data**: Delete datasets (requires `data_admin` role + PAM elevation)

### 3. Test Multi-Tenant Isolation
- Select an agent from `acme-corp`
- Try accessing resources from `techstart-inc`
- Observe automatic denial due to tenant mismatch

### 4. Request Privilege Elevation
- Select an agent
- Click "Request Privilege Elevation"
- Attempt sensitive operations like `delete_data`
- See time-bound grants in action

### 5. View Audit Trail
- All actions are automatically logged
- Cryptographic signatures ensure integrity
- Evidence chain validation proves tamper-resistance

## 🔧 Configuration

### Environment Variables (Vercel)

No environment variables required! The demo works out-of-the-box.

For production deployments, consider setting:
- `SIGNING_SECRET`: Custom secret for evidence vault signatures
- `COMPLIANCE_FRAMEWORKS`: Comma-separated list (default: HIPAA,GDPR,SOX)

### Customization

Edit `api/index.py` to:
- Add more agents and roles
- Configure different permissions
- Customize sensitive actions
- Add custom business logic

## 🎓 CIAF Concepts Demonstrated

### Role-Based Access Control (RBAC)
```python
analyst_role = RoleDefinition(
    name="data_analyst",
    permissions=[
        Permission(
            action="read_data",
            resource_type="dataset",
            condition=same_tenant_only
        )
    ]
)
```

### Attribute-Based Access Control (ABAC)
```python
# Conditions evaluate agent and resource attributes
condition=same_tenant_only  # Checks agent.tenant_id == resource.owner_tenant
```

### Privilege Elevation (PAM)
```python
grant = pam.create_grant(
    principal_id="agent-001",
    elevated_role="data_admin",
    duration_minutes=30,
    approved_by="manager",
    ticket_reference="TICKET-001"
)
```

### Evidence Chain
```python
# All actions generate cryptographically signed receipts
receipt = vault.get_receipt(receipt_id)
is_valid = vault.verify_chain()  # Verifies entire chain integrity
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/init` | POST | Initialize CIAF system |
| `/api/agents` | GET | List available agents |
| `/api/roles` | GET | List roles and permissions |
| `/api/execute` | POST | Execute action with authorization |
| `/api/elevate` | POST | Request privilege elevation |
| `/api/audit` | GET | Get audit trail |

## 🛠️ Technology Stack

- **Backend**: Python 3.9+ with Flask
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Styling**: Custom CSS with modern gradients
- **Deployment**: Vercel Serverless Functions
- **Security**: CIAF v1.3.1 framework

## 📝 CIAF Integration Example

```python
from ciaf.agents import (
    IAMStore, PAMStore, PolicyEngine, 
    EvidenceVault, ToolExecutor
)

# Initialize
iam = IAMStore()
pam = PAMStore()
vault = EvidenceVault(signing_secret="your-secret")
policy = PolicyEngine(iam, pam, sensitive_actions={"delete"})
executor = ToolExecutor(policy, vault, pam)

# Create identity
agent = Identity(
    principal_id="my-agent",
    principal_type=PrincipalType.AGENT,
    roles={"analyst"},
    tenant_id="my-company"
)
iam.add_identity(agent)

# Execute with authorization
result = executor.execute_tool("read_data", request)
if result.allowed:
    print(f"Success: {result.result}")
```

## 🔒 Security Notes

This is a **demonstration application**. For production use:

1. **Use strong signing secrets** for the Evidence Vault
2. **Implement proper authentication** for API endpoints
3. **Add rate limiting** to prevent abuse
4. **Store state persistently** (use databases instead of in-memory)
5. **Enable HTTPS** everywhere
6. **Review compliance requirements** for your specific use case

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📖 Resources

- [CIAF Documentation](https://github.com/yourusername/ciaf/docs)
- [Developer Guide](https://github.com/yourusername/ciaf/docs/agents/DEVELOPER_GUIDE.md)
- [Example Scenarios](https://github.com/yourusername/ciaf/examples)

## 📄 License

MIT License - see LICENSE file for details

## 🙋 Support

- GitHub Issues: [Report a bug](https://github.com/yourusername/ciaf/issues)
- Documentation: [Read the docs](https://github.com/yourusername/ciaf/docs)
- Email: support@yourcompany.com

---

Built with ❤️ using CIAF v1.3.1
