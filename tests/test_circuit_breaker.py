"""
Test the circuit breaker by simulating tool failures.
Run this SEPARATELY from the agent (not inside it).
"""

from agent_os.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
import time

print("=" * 60)
print("Circuit Breaker Test")
print("=" * 60)

config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout_seconds=5.0)
cb = CircuitBreaker(config=config)

print(f"\n1. Initial state: {cb.state} (failures={cb.failure_count})")
print("   → CLOSED means tool calls pass through normally\n")

print("2. Simulating 2 failures...")
cb.record_failure()
print(f"   After failure 1: state={cb.state}, failures={cb.failure_count}")
cb.record_failure()
print(f"   After failure 2: state={cb.state}, failures={cb.failure_count}")
print("   → Still CLOSED — haven't hit threshold yet\n")

print("3. One more failure (hits threshold)...")
cb.record_failure()
print(f"   After failure 3: state={cb.state}, failures={cb.failure_count}")
print("   → OPEN! All calls to this tool would be BLOCKED now\n")

print("4. Waiting 6 seconds for recovery window...")
time.sleep(6)
state = cb.get_state()
print(f"   After waiting: state={state}")
print("   → HALF_OPEN — one test call is allowed through\n")

print("5. Test call succeeds...")
cb.record_success()
print(f"   After success: state={cb.state}, failures={cb.failure_count}")
print("   → CLOSED again! Tool is healthy.\n")

print("=" * 60)
print("Circuit breaker lifecycle complete: CLOSED → OPEN → HALF_OPEN → CLOSED")