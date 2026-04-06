# Solution Report HTML Template Guide

When generating solution content for `generate_solution_report`, use the following HTML structure:

```html
<h2>Code Changes</h2>
<p>Description of what needs to change and why.</p>
<h3>Before</h3>
<pre><code>
# Original problematic code
DB_HOST = "localhost:5432"
</code></pre>
<h3>After</h3>
<pre><code>
# Fixed code using environment variables
import os
DB_HOST = os.environ.get("DB_HOST", "localhost:5432")
</code></pre>
<p>Explanation of the change.</p>

<h2>Dependencies</h2>
<ul>
  <li><strong>New package:</strong> <code>python-dotenv</code> - for loading .env files in development</li>
  <li><strong>requirements.txt change:</strong> Add <code>python-dotenv==1.0.0</code></li>
</ul>

<h2>Infrastructure / Configuration</h2>
<ul>
  <li>Create a Kubernetes ConfigMap for non-sensitive config</li>
  <li>Create a Kubernetes Secret for database credentials</li>
  <li>Update deployment manifest to mount env vars from ConfigMap/Secret</li>
</ul>
<h3>Example ConfigMap</h3>
<pre><code>
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DB_HOST: "cloud-sql-proxy:5432"
  LOG_LEVEL: "INFO"
</code></pre>

<h2>Effort Estimation</h2>
<div class="highlight">
  <strong>Effort: Medium (1-3 days)</strong>
  <p>Requires updating configuration management across the codebase and setting up cloud infrastructure.</p>
</div>

<h2>Potential Risks</h2>
<ul>
  <li><strong>Runtime failures</strong> if environment variables are not set correctly in deployment</li>
  <li><strong>Local development impact</strong> - developers will need .env files or local config</li>
  <li><strong>Testing</strong> - update tests to mock environment variables</li>
</ul>
```

## Guidelines

- Always show **before/after** code snippets for code changes
- Be **specific** - reference actual files and line numbers when possible
- Include **Kubernetes manifests** or **Docker changes** when applicable
- Categorize effort as: **Low** (< 1 day), **Medium** (1-3 days), **High** (> 3 days)
- List **concrete risks**, not generic warnings
