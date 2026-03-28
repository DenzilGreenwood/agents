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
    "force_mock_mode": False,  # Force mock mode if CIAF has runtime issues
}


def initialize_ciaf():
    """Initialize CIAF components"""
    global CIAF_AVAILABLE
    
    if _state["initialized"]:
        return

    if not CIAF_AVAILABLE:
        _state["initialized"] = True
        return

    try:
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
    except Exception as e:
        print(f"Warning: Failed to initialize CIAF components: {e}")
        print("Falling back to mock mode")
        CIAF_AVAILABLE = False
        _state["initialized"] = True
        return

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
    for identity in _state["iam"]._identities.values():
        if identity.principal_type == PrincipalType.AGENT:
            # Convert all non-serializable types to serializable ones
            agent_data = {
                "id": str(identity.principal_id),
                "name": str(identity.display_name),
                "tenant": str(identity.tenant_id),
                "roles": list(identity.roles) if identity.roles else [],
                "attributes": dict(identity.attributes) if identity.attributes else {}
            }
            agents.append(agent_data)

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

    # Use mock mode if CIAF unavailable or forcing mock mode
    if not CIAF_AVAILABLE or _state.get("force_mock_mode", False):
        # Mock response
        allowed = resource_tenant == (
            "acme-corp" if agent_id == "agent-demo-001" else "techstart-inc"
        )
        
        mock_result = {
            "success": True,
            "allowed": allowed,
            "executed": allowed,
            "reason": "Tenant mismatch - agent cannot access resources from different tenant" if not allowed else "Authorization granted",
            "mock_mode": True,
        }
        
        if allowed:
            # Generate mock tool output
            if action == "read_data":
                mock_result["result"] = {
                    "tool_output": {
                        "dataset_id": str(resource_id),
                        "records": 15000,
                        "columns": ["id", "timestamp", "value", "category"],
                        "status": "success",
                        "timestamp": datetime.now().isoformat()
                    },
                    "receipt_id": f"mock-receipt-{datetime.now().timestamp()}"
                }
            elif action == "export_report":
                mock_result["result"] = {
                    "tool_output": {
                        "report_id": str(resource_id),
                        "format": "PDF",
                        "pages": 42,
                        "exported_at": datetime.now().isoformat(),
                        "download_url": f"/downloads/{resource_id}.pdf"
                    },
                    "receipt_id": f"mock-receipt-{datetime.now().timestamp()}"
                }
            elif action == "delete_data":
                mock_result["result"] = {
                    "tool_output": {
                        "dataset_id": str(resource_id),
                        "deleted_records": 15000,
                        "status": "deleted",
                        "timestamp": datetime.now().isoformat()
                    },
                    "receipt_id": f"mock-receipt-{datetime.now().timestamp()}"
                }
        
        # Log mock execution
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_id,
            "action": action,
            "resource": resource_id,
            "allowed": allowed,
            "executed": allowed,
            "reason": mock_result["reason"]
        }
        _state["execution_log"].append(log_entry)
        
        return jsonify(mock_result)

    try:
        # Get agent identity
        agent = _state["iam"].get_identity(agent_id)
        if not agent:
            return jsonify({"success": False, "error": "Agent not found"}), 404

        # Create resource
        resource = Resource(
            resource_id=str(resource_id),
            resource_type="dataset" if "dataset" in str(resource_id) else "report",
            owner_tenant=str(resource_tenant),
            attributes={"classification": "confidential"},
        )

        # Create action request
        request_obj = ActionRequest(
            action=str(action),
            resource=resource,
            params={
                "dataset_id" if "dataset" in str(resource_id) else "report_id": str(resource_id)
            },
            justification=str(justification),
            requested_by=agent,
            correlation_id=f"web-demo-{datetime.now().timestamp()}",
        )

        # Execute
        result = _state["executor"].execute_tool(str(action), request_obj)

        # Log execution
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": str(agent.display_name),
            "action": str(action),
            "resource": str(resource_id),
            "allowed": result.allowed,
            "executed": result.executed,
            "reason": str(result.reason) if result.reason else "",
        }
        _state["execution_log"].append(log_entry)

        return jsonify(
            {
                "success": True,
                "allowed": result.allowed,
                "executed": result.executed,
                "reason": str(result.reason) if result.reason else "",
                "result": result.result if result.executed else None,
                "obligations": (
                    list(result.policy_obligations)
                    if hasattr(result, "policy_obligations")
                    else []
                ),
            }
        )

    except (TypeError, AttributeError) as e:
        error_msg = str(e)
        if "must be encoded before hashing" in error_msg or "encode" in error_msg:
            # Automatically enable mock mode for future requests
            _state["force_mock_mode"] = True
            print(f"Warning: CIAF execution failed ({error_msg}). Enabling mock mode.")
            
            # Retry with mock mode
            return execute_action()
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Execution error: {error_details}")
        
        # If it's a CIAF-related error, enable mock mode
        if "ciaf" in error_details.lower() or "evidence" in error_details.lower():
            _state["force_mock_mode"] = True
            print("Enabling mock mode due to CIAF error")
            return execute_action()
        
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
    for role in _state["iam"]._roles.values():
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
