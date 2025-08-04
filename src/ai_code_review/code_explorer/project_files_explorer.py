"""CodeExplorer class to explore project directory and retrieve code files."""

from pathlib import Path

MAX_FILE_SIZE = 1_048_576  # 1MB


class ProjectFileExplorer:
    """Explores the project directory and retrieves every code files with specified extensions."""

    def __init__(
        self,
        project_root: str | Path,
        extensions: list[str] | None = None,
    ):
        self._project_root = Path(project_root)
        self._extensions = extensions or ["py"]

    def explore(self) -> str:
        """Explores the project directory and returns a list of files with specified extensions."""
        codes = []
        for file in self._project_root.rglob("*"):
            if file.is_file() and file.suffix[1:] in self._extensions:
                try:
                    if file.stat().st_size <= MAX_FILE_SIZE:
                        codes.append(f"File:{file}\nCode:\n{file.read_text(encoding='utf-8')}")
                    else:
                        codes.append(f"File:{file}\nCode:\n[Skipped: file too large ({file.stat().st_size} bytes)]")
                except Exception as e:
                    codes.append(f"File:{file}\nCode:\n[Error reading file: {e}]")
        return "\n\n".join(codes)
