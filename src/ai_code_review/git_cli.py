"""Execute git commands using subprocess."""

import subprocess


def _run_git_cmd(
    repo: str,
    *args: str,
) -> str:
    """Run a git command in the specified repository.

    Args:
        repo (str): Path to the git repository.
        *args (str): Arguments to pass to the git command.

    Returns:
        str: The output of the git command.

    Raises:
        RuntimeError: If the git command fails.

    """
    cmd = ["git", "-C", repo, *args]
    result = subprocess.run(
        cmd,
        check=False, capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def diff_patch(repo: str, base: str, head: str) -> str:
    """Get the diff patch between two commits in a git repository.

    Args:
        repo (str): Path to the git repository.
        base (str): The base commit hash or branch.
        head (str): The head commit hash or branch.

    Returns:
        str: The diff patch between the two commits.

    """
    return _run_git_cmd(repo, "diff", "-p", "-U3", "-M", "-C", f"{base}...{head}")


def file_patch(repo: str, base: str, head: str, file_path: str) -> str:
    """Get the diff patch for a specific file between two commits in a git repository.

    Args:
        repo (str): Path to the git repository.
        base (str): The base commit hash or branch.
        head (str): The head commit hash or branch.
        file_path (str): The path to the file in the repository.

    Returns:
        str: The diff patch for the specified file.

    """
    return _run_git_cmd(repo, "diff", "-p", "-U3", "-M", "-C", f"{base}...{head}", "--", file_path)


def show_text(repo: str, rev: str, path: str) -> tuple[str, str | None]:
    ls_tree = _run_git_cmd(repo, "ls-tree", rev, "--", path).strip()
    if not ls_tree:
        return "", None
    sha = ls_tree.split()[2] if len(ls_tree.split()) > 2 else None
    txt = _run_git_cmd(repo, "show", f"{rev}:{path}").strip()
    return txt, sha
