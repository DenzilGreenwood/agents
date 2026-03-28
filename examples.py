"""
CIAF Demo - Example Scenarios & Testing Script

This script demonstrates various CIAF scenarios that can be executed
via the web interface or API calls.

Usage:
    python examples.py             # Run all scenarios
    python examples.py --api-only  # Test API endpoints only
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"  # Change to your Vercel URL


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"     {details}")


class CIAFDemo:
    """CIAF Demo Test Suite"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def test_api_health(self):
        """Test API health check"""
        print_header("API Health Check")

        try:
            response = self.session.get(f"{self.base_url}/")
            data = response.json()

            passed = response.status_code == 200 and data.get("status") == "online"
            print_result(
                "API Health",
                passed,
                f"Status: {data.get('status')}, CIAF Available: {data.get('ciaf_available')}",
            )
            return passed
        except Exception as e:
            print_result("API Health", False, str(e))
            return False

    def test_initialization(self):
        """Test system initialization"""
        print_header("System Initialization")

        try:
            response = self.session.post(f"{self.base_url}/api/init")
            data = response.json()

            passed = data.get("success", False)
            print_result("Initialize CIAF", passed)
            return passed
        except Exception as e:
            print_result("Initialize CIAF", False, str(e))
            return False

    def test_get_agents(self):
        """Test retrieving agents"""
        print_header("Retrieve Agents")

        try:
            response = self.session.get(f"{self.base_url}/api/agents")
            data = response.json()

            agents = data.get("agents", [])
            passed = len(agents) >= 2

            print_result("Get Agents", passed, f"Found {len(agents)} agents")

            for agent in agents:
                print(
                    f"     - {agent['name']} ({agent['id']}) - Tenant: {agent['tenant']}"
                )

            return passed
        except Exception as e:
            print_result("Get Agents", False, str(e))
            return False

    def test_get_roles(self):
        """Test retrieving roles"""
        print_header("Retrieve Roles & Permissions")

        try:
            response = self.session.get(f"{self.base_url}/api/roles")
            data = response.json()

            roles = data.get("roles", [])
            passed = len(roles) >= 2

            print_result("Get Roles", passed, f"Found {len(roles)} roles")

            for role in roles:
                print(f"     - {role['name']}: {len(role['permissions'])} permissions")

            return passed
        except Exception as e:
            print_result("Get Roles", False, str(e))
            return False

    def test_successful_execution(self):
        """Test successful action execution (same tenant)"""
        print_header("Scenario 1: Successful Authorization")

        try:
            payload = {
                "agent_id": "agent-demo-001",
                "action": "read_data",
                "resource_id": "dataset-2026-q1",
                "resource_tenant": "acme-corp",  # Matches agent tenant
                "justification": "Q1 quarterly report analysis",
            }

            response = self.session.post(f"{self.base_url}/api/execute", json=payload)
            data = response.json()

            passed = (
                data.get("success", False)
                and data.get("allowed", False)
                and data.get("executed", False)
            )

            print_result(
                "Same-Tenant Access", passed, "Agent can access own tenant's data"
            )

            if passed:
                print(f"     Result: {json.dumps(data.get('result'), indent=8)}")

            return passed
        except Exception as e:
            print_result("Same-Tenant Access", False, str(e))
            return False

    def test_tenant_isolation(self):
        """Test multi-tenant isolation (cross-tenant denial)"""
        print_header("Scenario 2: Multi-Tenant Isolation")

        try:
            payload = {
                "agent_id": "agent-demo-001",  # acme-corp
                "action": "read_data",
                "resource_id": "dataset-sensitive",
                "resource_tenant": "techstart-inc",  # Different tenant!
                "justification": "Attempted cross-tenant access",
            }

            response = self.session.post(f"{self.base_url}/api/execute", json=payload)
            data = response.json()

            # Should be denied
            passed = data.get("success", False) and not data.get("allowed", True)

            print_result(
                "Tenant Boundary Enforcement",
                passed,
                f"Denied: {data.get('reason', 'Unknown')}",
            )

            return passed
        except Exception as e:
            print_result("Tenant Boundary Enforcement", False, str(e))
            return False

    def test_privilege_elevation(self):
        """Test privilege elevation workflow"""
        print_header("Scenario 3: Privilege Elevation")

        try:
            # Step 1: Try sensitive action without elevation (should fail)
            print("\n  Step 1: Attempt sensitive action without elevation...")

            payload = {
                "agent_id": "agent-demo-001",
                "action": "delete_data",
                "resource_id": "dataset-old",
                "resource_tenant": "acme-corp",
                "justification": "Data retention policy cleanup",
            }

            response = self.session.post(f"{self.base_url}/api/execute", json=payload)
            data = response.json()

            denied_before = not data.get("allowed", True)
            print_result(
                "  Pre-Elevation Denial",
                denied_before,
                f"Correctly denied: {data.get('reason', 'Unknown')}",
            )

            # Step 2: Request elevation
            print("\n  Step 2: Request privilege elevation...")

            elevation_payload = {
                "agent_id": "agent-demo-001",
                "elevated_role": "data_admin",
                "duration_minutes": 30,
                "ticket_reference": "DEMO-TICKET-2026-001",
            }

            response = self.session.post(
                f"{self.base_url}/api/elevate", json=elevation_payload
            )
            data = response.json()

            elevation_granted = data.get("success", False)
            print_result(
                "  Elevation Grant",
                elevation_granted,
                f"Grant ID: {data.get('grant_id', 'N/A')}",
            )

            # Step 3: Retry action with elevation (should succeed)
            if elevation_granted:
                print("\n  Step 3: Retry sensitive action with elevation...")
                time.sleep(1)  # Small delay

                response = self.session.post(
                    f"{self.base_url}/api/execute", json=payload
                )
                data = response.json()

                allowed_after = data.get("allowed", False)
                print_result(
                    "  Post-Elevation Success",
                    allowed_after,
                    "Sensitive action now allowed with elevated privileges",
                )

                return denied_before and elevation_granted and allowed_after

            return False

        except Exception as e:
            print_result("Privilege Elevation", False, str(e))
            return False

    def test_audit_trail(self):
        """Test audit trail retrieval and verification"""
        print_header("Scenario 4: Audit Trail & Evidence Chain")

        try:
            response = self.session.get(f"{self.base_url}/api/audit")
            data = response.json()

            total_actions = data.get("total_actions", 0)
            chain_valid = data.get("chain_valid", False)
            recent_actions = data.get("recent_actions", [])

            passed = total_actions > 0 and chain_valid

            print_result(
                "Audit Trail Retrieval",
                passed,
                f"Total actions: {total_actions}, Chain valid: {chain_valid}",
            )

            print("\n  Recent Actions:")
            for action in recent_actions[-5:]:
                status = "✓" if action.get("allowed", False) else "✗"
                print(
                    f"     {status} {action.get('action', 'unknown')} by {action.get('agent', 'unknown')}"
                )

            return passed

        except Exception as e:
            print_result("Audit Trail", False, str(e))
            return False

    def test_export_report(self):
        """Test export report action"""
        print_header("Scenario 5: Export Report")

        try:
            payload = {
                "agent_id": "agent-demo-002",  # techstart-inc agent
                "action": "export_report",
                "resource_id": "report-annual-2026",
                "resource_tenant": "techstart-inc",
                "justification": "Annual business review",
            }

            response = self.session.post(f"{self.base_url}/api/execute", json=payload)
            data = response.json()

            passed = (
                data.get("success", False)
                and data.get("allowed", False)
                and data.get("executed", False)
            )

            print_result("Report Export", passed, "Report generated successfully")

            if passed and data.get("result"):
                result = data["result"].get("tool_output", {})
                print(f"     Report ID: {result.get('report_id')}")
                print(f"     Format: {result.get('format')}")
                print(f"     Pages: {result.get('pages')}")

            return passed

        except Exception as e:
            print_result("Report Export", False, str(e))
            return False

    def run_all_tests(self):
        """Run complete test suite"""
        print("\n")
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║                                                                   ║")
        print("║         CIAF Agentic Workflow - Automated Test Suite             ║")
        print("║                                                                   ║")
        print("╔═══════════════════════════════════════════════════════════════════╝")
        print(f"║  Testing: {self.base_url}")
        print("╚═══════════════════════════════════════════════════════════════════╗")

        results = {}

        # Run tests in sequence
        results["health"] = self.test_api_health()

        if results["health"]:
            results["init"] = self.test_initialization()
            results["agents"] = self.test_get_agents()
            results["roles"] = self.test_get_roles()
            results["execution"] = self.test_successful_execution()
            results["isolation"] = self.test_tenant_isolation()
            results["elevation"] = self.test_privilege_elevation()
            results["export"] = self.test_export_report()
            results["audit"] = self.test_audit_trail()

        # Summary
        print_header("Test Summary")

        total = len(results)
        passed = sum(1 for v in results.values() if v)

        print(f"\n  Tests Run: {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {total - passed}")
        print(f"  Success Rate: {(passed/total)*100:.1f}%\n")

        if passed == total:
            print("  🎉 All tests passed! Your CIAF demo is working perfectly.\n")
        else:
            print("  ⚠️  Some tests failed. Check the output above for details.\n")

        print("=" * 70)
        print()


if __name__ == "__main__":
    import sys

    # Check for custom base URL
    base_url = BASE_URL
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        base_url = sys.argv[1]

    print(f"\nℹ️  Testing CIAF Demo at: {base_url}")
    print("   (Change BASE_URL in script or pass as argument)\n")

    demo = CIAFDemo(base_url=base_url)
    demo.run_all_tests()
