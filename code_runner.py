import subprocess
import tempfile
import os

def run_python_code(source_code: str) -> str:
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".py",
            mode="w",
            encoding="utf-8"
        ) as temp_file:
            temp_file.write(source_code)
            temp_path = temp_file.name

        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if stdout:
            return stdout
        if stderr:
            return stderr

        return "No output."

    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out."
    except Exception as e:
        return f"Error: {e}"
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)