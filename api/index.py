"""
CIAF Agentic Workflow Demo API
Vercel Serverless Function
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Import CIAF components
try:
    from ciaf.agents import (
        IAMStore,
        PAMStore,
        PolicyEngine,
        EvidenceVault,
        ToolExecutor,
        RoleDefinition,
        Permission,
        Identity,
        PrincipalType,
        ActionRequest,
        Resource,
        same_tenant_only,
    )

    CIAF_AVAILABLE = True
except ImportError:
    CIAF_AVAILABLE = False
    print("Warning: CIAF not available. Using mock mode.")

# Global state (in production, use proper state management)
_state = {
    "initialized": False,
    "iam": None,
    "pam": None,
    "vault": None,
    "policy": None,
    "executor": None,
    "execution_log": [],
}


def initialize_ciaf():
    """Initialize CIAF components"""
    if _state["initialized"]:
        return

    if not CIAF_AVAILABLE:
        _state["initialized"] = True
        return

    # Initialize components
    _state["iam"] = IAMStore()
    _state["pam"] = PAMStore()
    _state["vault"] = EvidenceVault(signing_secret="demo-secret-key-2026")
    _state["policy"] = PolicyEngine(
        _state["iam"],
        _state["pam"],
        sensitive_actions={"delete_data", "export_pii"},
        compliance_frameworks=["HIPAA", "GDPR"],
    )
    _state["executor"] = ToolExecutor(_state["policy"], _state["vault"], _state["pam"])

    # Define roles
    analyst_role = RoleDefinition(
        name="data_analyst",
        permissions=[
            Permission(
                action="read_data",
                resource_type="dataset",
                condition=same_tenant_only,
                description="Read datasets from same tenant",
            ),
            Permission(
                action="export_report",
                resource_type="report",
                condition=same_tenant_only,
                description="Export reports from same tenant",
            ),
        ],
    )

    admin_role = RoleDefinition(
        name="data_admin",
        permissions=[
            Permission(
                action="read_data",
                resource_type="dataset",
                condition=same_tenant_only,
                description="Read datasets from same tenant",
            ),
            Permission(
                action="delete_data",
                resource_type="dataset",
                condition=same_tenant_only,
                description="Delete datasets from same tenant",
            ),
            Permission(
                action="export_pii",
                resource_type="dataset",
                condition=same_tenant_only,
                description="Export PII data",
            ),
        ],
    )

    _state["iam"].add_role(analyst_role)
    _state["iam"].add_role(admin_role)

    # Create demo agents
    agent1 = Identity(
        principal_id="agent-demo-001",
        principal_type=PrincipalType.AGENT,
        display_name="Analytics Agent Alpha",
        roles={"data_analyst"},
        attributes={"tenant": "acme-corp", "team": "analytics"},
        tenant_id="acme-corp",
        environment="production",
    )

    agent2 = Identity(
        principal_id="agent-demo-002",
        principal_type=PrincipalType.AGENT,
        display_name="Analytics Agent Beta",
        roles={"data_analyst"},
        attributes={"tenant": "techstart-inc", "team": "data-science"},
        tenant_id="techstart-inc",
        environment="production",
    )

    _state["iam"].add_identity(agent1)
    _state["iam"].add_identity(agent2)

    # Register tools
    def read_data_tool(dataset_id: str):
        return {
            "dataset_id": dataset_id,
            "records": 15000,
            "columns": ["id", "timestamp", "value", "category"],
            "status": "success",
            "timestamp": datetime.now().isoformat(),
        }

    def export_report_tool(report_id: str):
        return {
            "report_id": report_id,
            "format": "PDF",
            "pages": 42,
            "exported_at": datetime.now().isoformat(),
            "download_url": f"/downloads/{report_id}.pdf",
        }

    def delete_data_tool(dataset_id: str):
        return {
            "dataset_id": dataset_id,
            "deleted_records": 15000,
            "status": "deleted",
            "timestamp": datetime.now().isoformat(),
        }

    _state["executor"].register_tool("read_data", read_data_tool)
    _state["executor"].register_tool("export_report", export_report_tool)
    _state["executor"].register_tool("delete_data", delete_data_tool)

    _state["initialized"] = True


@app.route("/")
def index():
    """Health check"""
    return jsonify(
        {
            "status": "online",
            "service": "CIAF Agentic Workflow Demo",
            "ciaf_available": CIAF_AVAILABLE,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/init", methods=["POST"])
def init_system():
    """Initialize the CIAF system"""
    try:
        initialize_ciaf()
        return jsonify(
            {
                "success": True,
                "message": "CIAF system initialized",
                "ciaf_available": CIAF_AVAILABLE,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/agents", methods=["GET"])
def get_agents():
    """Get list of available agents"""
    initialize_ciaf()

    if not CIAF_AVAILABLE:
        return jsonify(
            {
                "agents": [
                    {
                        "id": "agent-demo-001",
                        "name": "Analytics Agent Alpha",
                        "tenant": "acme-corp",
                        "roles": ["data_analyst"],
                    },
                    {
                        "id": "agent-demo-002",
                        "name": "Analytics Agent Beta",
                        "tenant": "techstart-inc",
                        "roles": ["data_analyst"],
                    },
                ]
            }
        )

    agents = []
    for identity in _state["iam"].identities.values():
        if identity.principal_type == PrincipalType.AGENT:
            agents.append(
                {
                    "id": identity.principal_id,
                    "name": identity.display_name,
                    "tenant": identity.tenant_id,
                    "roles": list(identity.roles),
                    "attributes": identity.attributes,
                }
            )

    return jsonify({"agents": agents})


@app.route("/api/execute", methods=["POST"])
def execute_action():
    """Execute an action with CIAF authorization"""
    initialize_ciaf()

    data = request.get_json()
    agent_id = data.get("agent_id")
    action = data.get("action")
    resource_id = data.get("resource_id")
    resource_tenant = data.get("resource_tenant")
    justification = data.get("justification", "Demo execution")

    if not CIAF_AVAILABLE:
        # Mock response
        allowed = resource_tenant == (
            "acme-corp" if agent_id == "agent-demo-001" else "techstart-inc"
        )
        return jsonify(
            {
                "success": True,
                "allowed": allowed,
                "executed": allowed,
                "reason": "Tenant mismatch" if not allowed else "Success",
                "mock_mode": True,
                "result": {"message": "This is a mock execution"} if allowed else None,
            }
        )

    try:
        # Get agent identity
        agent = _state["iam"].get_identity(agent_id)
        if not agent:
            return jsonify({"success": False, "error": "Agent not found"}), 404

        # Create resource
        resource = Resource(
            resource_id=resource_id,
            resource_type="dataset" if "dataset" in resource_id else "report",
            owner_tenant=resource_tenant,
            attributes={"classification": "confidential"},
        )

        # Create action request
        request_obj = ActionRequest(
            action=action,
            resource=resource,
            params={
                "dataset_id" if "dataset" in resource_id else "report_id": resource_id
            },
            justification=justification,
            requested_by=agent,
            correlation_id=f"web-demo-{datetime.now().timestamp()}",
        )

        # Execute
        result = _state["executor"].execute_tool(action, request_obj)

        # Log execution
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent.display_name,
            "action": action,
            "resource": resource_id,
            "allowed": result.allowed,
            "executed": result.executed,
            "reason": result.reason,
        }
        _state["execution_log"].append(log_entry)

        return jsonify(
            {
                "success": True,
                "allowed": result.allowed,
                "executed": result.executed,
                "reason": result.reason,
                "result": result.result if result.executed else None,
                "obligations": (
                    list(result.policy_obligations)
                    if hasattr(result, "policy_obligations")
                    else []
                ),
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/elevate", methods=["POST"])
def create_elevation():
    """Create a privilege elevation grant"""
    initialize_ciaf()

    data = request.get_json()
    agent_id = data.get("agent_id")
    elevated_role = data.get("elevated_role", "data_admin")
    duration = data.get("duration_minutes", 30)
    ticket = data.get("ticket_reference", "DEMO-TICKET-001")

    if not CIAF_AVAILABLE:
        return jsonify(
            {
                "success": True,
                "grant_id": f"grant-mock-{datetime.now().timestamp()}",
                "mock_mode": True,
            }
        )

    try:
        grant = _state["pam"].create_grant(
            principal_id=agent_id,
            elevated_role=elevated_role,
            duration_minutes=duration,
            approved_by="demo-manager",
            ticket_reference=ticket,
            purpose="Demo elevation for sensitive operation",
        )

        return jsonify(
            {
                "success": True,
                "grant_id": grant.grant_id,
                "expires_at": grant.expires_at.isoformat(),
                "elevated_role": elevated_role,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/audit", methods=["GET"])
def get_audit_trail():
    """Get audit trail"""
    initialize_ciaf()

    if not CIAF_AVAILABLE:
        return jsonify(
            {
                "total_actions": len(_state["execution_log"]),
                "recent_actions": _state["execution_log"][-10:],
                "chain_valid": True,
                "mock_mode": True,
            }
        )

    try:
        receipts = _state["vault"].get_all_receipts()
        chain_valid = _state["vault"].verify_chain()

        recent_receipts = []
        for receipt in receipts[-10:]:
            recent_receipts.append(
                {
                    "receipt_id": receipt.receipt_id,
                    "action": receipt.action,
                    "agent": receipt.principal_id,
                    "resource": receipt.resource_id,
                    "timestamp": receipt.timestamp.isoformat(),
                    "allowed": receipt.allowed,
                    "hash": receipt.get_receipt_hash()[:16] + "...",
                }
            )

        return jsonify(
            {
                "total_actions": len(receipts),
                "recent_actions": recent_receipts,
                "chain_valid": chain_valid,
                "execution_log": _state["execution_log"][-10:],
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/roles", methods=["GET"])
def get_roles():
    """Get available roles"""
    initialize_ciaf()

    if not CIAF_AVAILABLE:
        return jsonify(
            {
                "roles": [
                    {
                        "name": "data_analyst",
                        "permissions": [
                            {"action": "read_data", "resource_type": "dataset"},
                            {"action": "export_report", "resource_type": "report"},
                        ],
                    },
                    {
                        "name": "data_admin",
                        "permissions": [
                            {"action": "read_data", "resource_type": "dataset"},
                            {"action": "delete_data", "resource_type": "dataset"},
                            {"action": "export_pii", "resource_type": "dataset"},
                        ],
                    },
                ]
            }
        )

    roles = []
    for role in _state["iam"].roles.values():
        permissions = []
        for perm in role.permissions:
            permissions.append(
                {
                    "action": perm.action,
                    "resource_type": perm.resource_type,
                    "description": perm.description,
                }
            )
        roles.append({"name": role.name, "permissions": permissions})

    return jsonify({"roles": roles})


# Vercel serverless handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
