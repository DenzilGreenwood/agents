# CIAF Demo - User Guide

## Welcome! 👋

This interactive demo showcases **CIAF v1.3.1** (Contextual Identity and Authorization Framework) - an enterprise-grade authorization framework for AI agents and autonomous systems.

## What is CIAF?

CIAF provides:

- **🔐 Identity & Access Management**: Role-based permissions with attribute conditions
- **🏢 Multi-Tenant Isolation**: Automatic boundary enforcement between tenants
- **⚡ Privilege Elevation**: Time-bound, audited access to sensitive operations
- **📜 Evidence Vault**: Cryptographically signed, tamper-proof audit trails
- **✅ Compliance**: Built-in HIPAA, GDPR, SOX obligation tracking

## How to Use This Demo

### 1️⃣ Understanding Agents

The demo includes two AI agents:

- **🤖 Analytics Agent Alpha**
  - Tenant: `acme-corp`
  - Role: `data_analyst`
  - Can: Read data, Export reports (from acme-corp only)

- **🤖 Analytics Agent Beta**
  - Tenant: `techstart-inc`
  - Role: `data_analyst`
  - Can: Read data, Export reports (from techstart-inc only)

**Key Concept**: Each agent is bound to a specific tenant and can ONLY access resources owned by that tenant.

### 2️⃣ Executing Actions

#### Step-by-Step:

1. **Select an Agent**: Click on agent card or use dropdown
2. **Choose an Action**:
   - `read_data` - Read a dataset
   - `export_report` - Generate a report
   - `delete_data` - Delete data (requires elevation!)
3. **Enter Resource ID**: e.g., `dataset-2026-q1`
4. **Select Resource Tenant**: Must match agent's tenant for success
5. **Provide Justification**: Business reason for the action
6. **Click "Execute Action"**

#### What Happens:

1. CIAF checks if agent has required role
2. CIAF evaluates ABAC conditions (tenant match)
3. CIAF checks for privilege elevation if needed
4. Action executes if authorized
5. Evidence receipt is cryptographically signed
6. Result is displayed with full details

### 3️⃣ Try These Scenarios

#### ✅ Scenario 1: Successful Access

```
Agent: Analytics Agent Alpha
Action: Read Data
Resource ID: customer-data-2026
Resource Tenant: acme-corp
```

**Expected Result**: ✓ Success - Agent can access its own tenant's data

#### ❌ Scenario 2: Tenant Boundary Violation

```
Agent: Analytics Agent Alpha (acme-corp)
Action: Read Data
Resource ID: competitor-secrets
Resource Tenant: techstart-inc
```

**Expected Result**: ✗ Denied - Cannot access another tenant's data

#### 🔐 Scenario 3: Privilege Elevation Required

```
Agent: Analytics Agent Alpha
Action: Delete Data
Resource ID: old-dataset
Resource Tenant: acme-corp
```

**Expected Result**: ✗ Denied - Requires elevated privileges

**Solution**:
1. Click "Request Privilege Elevation"
2. Wait for grant approval (instant in demo)
3. Retry the Delete Data action
4. **Expected**: ✓ Success - Elevated privileges granted for 30 minutes

### 4️⃣ Understanding Roles & Permissions

The demo includes two roles:

#### 📊 Data Analyst (Standard Access)
- ✓ Read Data from same tenant
- ✓ Export Reports from same tenant
- ✗ Delete Data
- ✗ Export PII

#### 🔧 Data Admin (Elevated Access)
- ✓ Read Data from same tenant
- ✓ Delete Data from same tenant
- ✓ Export PII from same tenant

**Important**: Sensitive operations (delete, export PII) require **Privilege Elevation** even if the agent has the right role.

### 5️⃣ Viewing the Audit Trail

Every action creates an immutable audit record.

**Features**:
- **Cryptographic Signatures**: Each receipt is signed
- **Chain Verification**: Entire chain proves no tampering
- **Complete Context**: Agent, action, resource, outcome, timestamp
- **Compliance Ready**: Satisfies regulatory requirements

**How to View**:
1. Scroll to "Audit Trail & Evidence Chain" section
2. Click "Refresh Audit Trail"
3. See recent actions with full details
4. Check "Chain Status: ✓ Valid" badge

**What You See**:
- Green entries (✓ Allowed) - Successful authorizations
- Red entries (✗ Denied) - Rejected attempts
- Timestamps, agent names, resources
- Denial reasons for failed attempts

### 6️⃣ Understanding ABAC (Attribute-Based Access Control)

CIAF uses attributes to make fine-grained decisions:

**Agent Attributes**:
- `tenant_id`: Which tenant owns the agent
- `team`: Which team the agent belongs to
- `environment`: prod/staging/dev

**Resource Attributes**:
- `owner_tenant`: Which tenant owns the resource
- `classification`: confidential/public/restricted

**Conditions**:
- `same_tenant_only`: Ensures `agent.tenant_id == resource.owner_tenant`

### 7️⃣ Code Examples

Use the code tabs at the bottom to see:
- **Setup**: How to initialize CIAF
- **Execution**: How to execute authorized actions
- **Elevation**: How to request and use privilege grants

Copy and adapt these examples for your own projects!

## Real-World Use Cases

### Healthcare
```
Agent: Claims Processing Bot
Action: Access patient records
Condition: Same healthcare provider + HIPAA logging
```

### Finance
```
Agent: Trading Algorithm
Action: Execute trade
Condition: Within risk limits + SOX compliance
```

### Multi-Tenant SaaS
```
Agent: Customer Analytics Bot
Action: Generate insights
Condition: Only from customer's own data
```

## Key Concepts Explained

### 🆔 Identity
Every agent has:
- Unique ID
- Display name
- Assigned roles
- Tenant binding
- Custom attributes

### 🎭 Role
Collections of permissions:
- Named (e.g., "analyst", "admin")
- Contains multiple permissions
- Can be elevated temporarily

### ✅ Permission
Specific grants:
- Action (what to do)
- Resource type (what to do it on)
- Condition (when it's allowed)

### 🔐 Privilege Elevation (PAM)
Temporary, audited access to sensitive operations:
- Time-bound (expires automatically)
- Requires approval reference
- Fully audited
- Just-in-time access

### 📜 Evidence Vault
Immutable audit log:
- Cryptographically signed receipts
- Chain-of-custody proof
- Tamper detection
- Compliance-ready records

## Best Practices

1. **Always Provide Justification**: Helps during audits
2. **Use Descriptive Resource IDs**: Makes logs readable
3. **Request Elevation Only When Needed**: Principle of least privilege
4. **Verify Audit Trail Regularly**: Chain should always be valid
5. **Test Tenant Boundaries**: Ensure isolation works

## Troubleshooting

### "Permission denied"
- Check agent has the required role
- Verify resource tenant matches agent tenant
- Try requesting privilege elevation

### "Action requires elevation"
- Click "Request Privilege Elevation" button
- Retry the action within 30 minutes

### "Chain status invalid"
- Refresh the page
- This shouldn't happen - indicates tampering

## Learn More

- **Quick Start Guide**: See main documentation
- **API Reference**: Check the code examples
- **GitHub Repository**: [Link to CIAF repo]
- **Developer Guide**: `docs/agents/DEVELOPER_GUIDE.md`

## Feedback

Have questions or suggestions? 
- Open an issue on GitHub
- Contact: support@yourcompany.com
- Join our Discord community

---

Enjoy exploring CIAF! 🚀
