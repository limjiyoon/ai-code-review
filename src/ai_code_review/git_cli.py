"""Execute git commands using subprocess."""

import subprocess

SHA_LOCATION = 2


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
        check=False,
        capture_output=True,
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
    if head == "HEAD":
        return _run_git_cmd(repo, "diff", "-p", "-U3", "-M", "-C", f"{base}")
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
    """Get the content of a file at a specific revision in a git repository.

    Args:
        repo (str): Path to the git repository.
        rev (str): The commit hash or branch name.
        path (str): The path to the file in the repository.

    Returns:
        tuple[str, str | None]: The content of the file and its SHA hash.

    """
    ls_tree = _run_git_cmd(repo, "ls-tree", rev, "--", path).strip()
    if not ls_tree:
        return "", None
    sha = ls_tree.split()[SHA_LOCATION] if len(ls_tree.split()) > SHA_LOCATION else None
    txt = _run_git_cmd(repo, "show", f"{rev}:{path}").strip()
    return txt, sha
