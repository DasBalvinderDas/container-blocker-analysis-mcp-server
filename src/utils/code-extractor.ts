import fs from "fs/promises";
import path from "path";
import os from "os";
import AdmZip from "adm-zip";
import { simpleGit } from "simple-git";

export interface ExtractedFile {
  relativePath: string;
  content: string;
  language: string;
}

const EXTENSION_TO_LANGUAGE: Record<string, string> = {
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
};

const EXCLUDE_DIRS = new Set([
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
]);

const EXCLUDE_FILES = new Set([
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
]);

function getLanguage(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  const basename = path.basename(filePath).toLowerCase();

  if (basename === "dockerfile" || basename.startsWith("dockerfile.")) {
    return "dockerfile";
  }
  if (basename === "docker-compose.yml" || basename === "docker-compose.yaml") {
    return "yaml";
  }
  if (basename === "makefile") return "makefile";

  return EXTENSION_TO_LANGUAGE[ext] || "";
}

function isTextFile(filePath: string): boolean {
  const ext = path.extname(filePath).toLowerCase();
  const basename = path.basename(filePath).toLowerCase();

  if (EXCLUDE_FILES.has(basename)) return false;

  // Include known code/config extensions
  if (EXTENSION_TO_LANGUAGE[ext]) return true;

  // Include common config files without extensions
  const knownNames = [
    "dockerfile",
    "makefile",
    "procfile",
    "gemfile",
    "rakefile",
    "vagrantfile",
  ];
  if (knownNames.includes(basename)) return true;

  return false;
}

async function walkDirectory(dir: string): Promise<ExtractedFile[]> {
  const files: ExtractedFile[] = [];

  async function walk(currentDir: string) {
    const entries = await fs.readdir(currentDir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);

      if (entry.isDirectory()) {
        if (!EXCLUDE_DIRS.has(entry.name)) {
          await walk(fullPath);
        }
      } else if (entry.isFile() && isTextFile(fullPath)) {
        try {
          const content = await fs.readFile(fullPath, "utf-8");
          if (content.trim()) {
            files.push({
              relativePath: path.relative(dir, fullPath),
              content,
              language: getLanguage(fullPath),
            });
          }
        } catch {
          // Skip unreadable files
        }
      }
    }
  }

  await walk(dir);
  return files;
}

export async function extractFromZip(zipPath: string): Promise<ExtractedFile[]> {
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "cba-zip-"));

  try {
    const zip = new AdmZip(zipPath);
    zip.extractAllTo(tmpDir, true);
    return await walkDirectory(tmpDir);
  } finally {
    await fs.rm(tmpDir, { recursive: true, force: true }).catch(() => {});
  }
}

export async function extractFromGitRepo(repoUrl: string): Promise<ExtractedFile[]> {
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "cba-git-"));

  try {
    const git = simpleGit();
    await git.clone(repoUrl, tmpDir, { "--depth": "1" });
    return await walkDirectory(tmpDir);
  } finally {
    await fs.rm(tmpDir, { recursive: true, force: true }).catch(() => {});
  }
}

export async function extractFromDirectory(dirPath: string): Promise<ExtractedFile[]> {
  return await walkDirectory(dirPath);
}

export function extractFromCodeBlock(code: string, language?: string): ExtractedFile[] {
  return [
    {
      relativePath: `provided_code.${getExtensionForLanguage(language || "plaintext")}`,
      content: code,
      language: language || "plaintext",
    },
  ];
}

function getExtensionForLanguage(lang: string): string {
  const langToExt: Record<string, string> = {
    python: "py",
    java: "java",
    javascript: "js",
    typescript: "ts",
    go: "go",
    rust: "rs",
    ruby: "rb",
    php: "php",
    csharp: "cs",
    cpp: "cpp",
    c: "c",
    swift: "swift",
    kotlin: "kt",
    scala: "scala",
    shell: "sh",
    plaintext: "txt",
  };
  return langToExt[lang] || "txt";
}

export function formatFilesForAnalysis(files: ExtractedFile[]): string {
  return files
    .map(
      (f) =>
        `--- File: ${f.relativePath} (${f.language}) ---\n${f.content}`
    )
    .join("\n\n");
}
