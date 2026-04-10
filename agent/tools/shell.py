"""
Tool: Execute Shell Command
Purpose: Lets the agent run arbitrary commands on the host machine.
Safety: DANGEROUS — this is intentionally included so we can test
        governance blocking it. In a real system, this tool should
        never exist without governance controls.
"""

import subprocess


def execute_shell(command: str) -> dict:
    """Execute a shell command on the host system.

    Args:
        command: The shell command to run (e.g., "ls -la /tmp").

    Returns:
        A dictionary with the command output.
    """
    print(f"    [TOOL EXECUTING] execute_shell(command='{command}')")

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10
        )
        return {
            "status": "success",
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "command": command, "error": "Command timed out"}
    except Exception as e:
        return {"status": "error", "command": command, "error": str(e)}