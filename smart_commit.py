#!/usr/bin/env python3
import subprocess
import sys
import os

def get_staged_files():
    """Get list of staged files using git diff --cached."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True
    )
    files = result.stdout.strip().split("\n")
    return [f for f in files if f]  # filter out empty strings

def detect_commit_type(files):
    """Guess commit type from file patterns."""
    if all(f.endswith(".md") for f in files):
        return "docs"
    if any("test" in f.lower() or f.startswith("tests") for f in files):
        return "test"
    if any(f.endswith(ext) for ext in [".py", ".js", ".ts", ".cpp", ".h"]):
        return "feat"
    if any(f.endswith(ext) for ext in ["package.json", "package-lock.json", "pyproject.toml"]):
        return "chore"
    return "chore"

def generate_summary(commit_type, files):
    """Generate the first line (title) of the commit message."""
    if len(files) == 1:
        filename = os.path.basename(files[0])
        name_without_ext = os.path.splitext(filename)[0]
        return f"{commit_type}({name_without_ext}): update {filename}"
    else:
        return f"{commit_type}: update {len(files)} files"

def generate_body(files):
    """Generate the body of the commit message with changed file list."""
    lines = [f"- Modified: {f}" for f in files]
    return "\n".join(lines)

def confirm_message(title, body):
    """Show user the message and ask for confirmation."""
    print("\nSuggested commit message:")
    print("-" * 40)
    print(title)
    print()
    print(body)
    print("-" * 40)
    choice = input("Proceed with this commit? [Y/n/edit]: ").strip().lower()
    if choice in ["", "y", "yes"]:
        return title, body
    elif choice == "edit":
        print("\nEnter your custom commit message (end with an empty line):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        full_message = "\n".join(lines)
        # Split into title/body for git commit
        parts = full_message.split("\n", 1)
        title = parts[0]
        body = parts[1] if len(parts) > 1 else ""
        return title, body
    else:
        print("❌ Commit canceled.")
        sys.exit(0)

def run_commit(title, body):
    """Execute git commit with the generated message."""
    cmd = ["git", "commit", "-m", title]
    if body.strip():
        cmd += ["-m", body]
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("✅ Commit created successfully.")
    else:
        print("❌ Git commit failed.")

def main():
    files = get_staged_files()
    if not files:
        print("⚠️ No staged changes found. Use 'git add' first.")
        sys.exit(1)

    commit_type = detect_commit_type(files)
    title = generate_summary(commit_type, files)
    body = generate_body(files)

    title, body = confirm_message(title, body)
    run_commit(title, body)

if __name__ == "__main__":
    main()
