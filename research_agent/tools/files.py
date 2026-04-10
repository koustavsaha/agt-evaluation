"""
Tool: Read File
Purpose: Lets the agent read files from the filesystem.
Safety: SAFE — read-only.
"""


def read_file(filepath: str) -> dict:
    """Read the contents of a file.

    Args:
        filepath: The path to the file to read (e.g., "/tmp/data.txt").

    Returns:
        A dictionary with the file contents, or an error message.
    """
    print(f"    [TOOL EXECUTING] read_file(filepath='{filepath}')")

    try:
        with open(filepath, "r") as f:
            content = f.read(2000)  # Limit to 2KB for safety
        return {"status": "success", "filepath": filepath, "content": content}
    except FileNotFoundError:
        return {"status": "error", "filepath": filepath, "error": "File not found"}
    except PermissionError:
        return {"status": "error", "filepath": filepath, "error": "Permission denied"}
    except Exception as e:
        return {"status": "error", "filepath": filepath, "error": str(e)}