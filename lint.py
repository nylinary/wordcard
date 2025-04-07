import os
import subprocess
import sys


def run_pre_commit():
    if sys.platform == "win32":
        # Windows command using PowerShell
        command = [
            "powershell",
            "-Command",
            (
                "cd $PWD; "
                "git diff --staged --name-only --diff-filter=d -- '*.py' | "
                "ForEach-Object { pre-commit run --files $_ }"
            ),
        ]
    elif sys.platform == "darwin" or sys.platform == "linux":  # macOS/Linux
        # macOS/Linux command
        command = [
            "bash",
            "-c",
            ("cd $(pwd); git diff --staged --name-only --diff-filter=d -z -- '*.py' | xargs -0 pre-commit run --files"),
        ]
    else:
        print("Unsupported OS")
        sys.exit(1)

    try:
        subprocess.run(command, check=True, cwd=os.getcwd())
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_pre_commit()
