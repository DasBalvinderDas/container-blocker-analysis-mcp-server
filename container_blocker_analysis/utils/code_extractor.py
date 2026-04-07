"""Utilities for extracting code from various sources (zip, directory, code block)."""

import os
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtractedFile:
    """Represents a single extracted source file."""

    relative_path: str
    content: str
    language: str


EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".html": "html",
    ".css": "css",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".sh": "shell",
    ".bash": "shell",
    ".dockerfile": "dockerfile",
    ".tf": "terraform",
    ".gradle": "gradle",
    ".properties": "properties",
    ".ini": "ini",
    ".cfg": "config",
    ".conf": "config",
    ".toml": "toml",
}

EXCLUDE_DIRS: set[str] = {
    "node_modules",
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "env",
    ".env",
    "build",
    "dist",
    ".idea",
    ".vscode",
    ".gradle",
    "target",
    "bin",
    "obj",
    ".next",
    ".nuxt",
    "vendor",
    ".terraform",
}

EXCLUDE_FILES: set[str] = {
    ".DS_Store",
    "Thumbs.db",
    ".gitignore",
    ".gitattributes",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Cargo.lock",
    "poetry.lock",
    "Gemfile.lock",
    "composer.lock",
}

KNOWN_FILENAMES: set[str] = {
    "dockerfile",
    "makefile",
    "procfile",
    "gemfile",
    "rakefile",
    "vagrantfile",
}


def get_language(file_path: str) -> str:
    """Detect programming language from file extension or name."""
    basename = os.path.basename(file_path).lower()

    if basename == "dockerfile" or basename.startswith("dockerfile."):
        return "dockerfile"
    if basename in ("docker-compose.yml", "docker-compose.yaml"):
        return "yaml"
    if basename == "makefile":
        return "makefile"

    ext = os.path.splitext(file_path)[1].lower()
    return EXTENSION_TO_LANGUAGE.get(ext, "")


def _is_text_file(file_path: str) -> bool:
    """Check if a file is a recognized text/code file."""
    basename = os.path.basename(file_path).lower()
    if basename in EXCLUDE_FILES:
        return False

    ext = os.path.splitext(file_path)[1].lower()
    if ext in EXTENSION_TO_LANGUAGE:
        return True

    if basename in KNOWN_FILENAMES:
        return True

    return False


def _walk_directory(root_dir: str) -> list[ExtractedFile]:
    """Recursively walk a directory and extract text/code files."""
    files: list[ExtractedFile] = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter out excluded directories in-place
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if not _is_text_file(full_path):
                continue
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if content.strip():
                    rel_path = os.path.relpath(full_path, root_dir)
                    files.append(
                        ExtractedFile(
                            relative_path=rel_path,
                            content=content,
                            language=get_language(full_path),
                        )
                    )
            except Exception:
                continue

    return files


def extract_from_zip(zip_path: str) -> list[ExtractedFile]:
    """Extract code files from a ZIP archive."""
    tmp_dir = tempfile.mkdtemp(prefix="cba-zip-")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_dir)
        return _walk_directory(tmp_dir)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def extract_from_directory(dir_path: str) -> list[ExtractedFile]:
    """Extract code files from a local directory."""
    return _walk_directory(dir_path)


def extract_from_code_block(code: str, language: Optional[str] = None) -> list[ExtractedFile]:
    """Wrap inline code into an ExtractedFile."""
    lang = language or "plaintext"
    lang_to_ext = {
        "python": "py", "java": "java", "javascript": "js", "typescript": "ts",
        "go": "go", "rust": "rs", "ruby": "rb", "php": "php", "csharp": "cs",
        "cpp": "cpp", "c": "c", "swift": "swift", "kotlin": "kt", "scala": "scala",
        "shell": "sh", "plaintext": "txt",
    }
    ext = lang_to_ext.get(lang, "txt")
    return [
        ExtractedFile(
            relative_path=f"provided_code.{ext}",
            content=code,
            language=lang,
        )
    ]


def format_files_for_analysis(files: list[ExtractedFile]) -> str:
    """Format extracted files into a single string for LLM analysis."""
    parts = []
    for f in files:
        parts.append(f"--- File: {f.relative_path} ({f.language}) ---\n{f.content}")
    return "\n\n".join(parts)
