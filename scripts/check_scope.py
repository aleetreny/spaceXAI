"""Reject changes outside the branch role, including local uncommitted files."""
import argparse
import fnmatch
import json
from pathlib import Path
import subprocess
import sys


def git(*args):
    return subprocess.check_output(["git", *args]).decode().strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--branch", default=None)
    args = parser.parse_args()
    branch = args.branch or git("branch", "--show-current")
    roles = json.loads(Path("coordination/roles.json").read_text())
    matches = [name for name, role in roles.items() if any(
        branch == prefix or branch.startswith(prefix + "/")
        for prefix in role["branches"])]
    if len(matches) != 1:
        sys.exit(f"Branch {branch!r}: use one role branch prefix from coordination/roles.json")
    role = matches[0]
    # No rename detection: both old and new paths must belong to the role.
    paths = set(git("diff", "--no-renames", "--name-only", "-z", args.base + "...HEAD").split("\0"))
    paths.update(git("diff", "--no-renames", "--name-only", "-z", "HEAD").split("\0"))
    paths.update(git("ls-files", "--others", "--exclude-standard", "-z").split("\0"))
    paths.discard("")
    forbidden = sorted(path for path in paths if not any(
        fnmatch.fnmatchcase(path, pattern) for pattern in roles[role]["paths"]))
    if forbidden:
        sys.exit(f"Role {role}: ask the owning contributor to change these files:\n" + "\n".join(forbidden))
    print(f"Scope OK: {role}, {len(paths)} files")


if __name__ == "__main__":
    main()
