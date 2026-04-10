"""Verify all AGT packages are installed and importable."""

print("=" * 60)
print("AGT Installation Verification")
print("=" * 60)

packages = [
    ("Agent OS (Policy Engine)",  "from agent_os import PolicyEngine"),
    ("Agent Mesh (Identity)",     "from agentmesh import AgentIdentity"),
    ("Agent SRE (Reliability)",   "from agent_os.circuit_breaker import CircuitBreaker"),
]

all_ok = True
for name, import_stmt in packages:
    try:
        exec(import_stmt)
        print(f"  ✓ {name}")
    except ImportError as e:
        print(f"  ✗ {name}: {e}")
        all_ok = False

print()
if all_ok:
    print("All core packages installed successfully.")
    print("You are ready to add governance to your agent.")
else:
    print("Some packages failed. Try: pip install agent-governance-toolkit[full]")