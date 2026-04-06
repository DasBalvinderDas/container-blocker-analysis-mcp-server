# Containerization Blocker Definitions

## 1. Hardcoded File Paths
**What to look for:** Absolute paths like `/var/log/`, `/etc/config/`, `/home/user/`, `C:\Users\`
**Why it matters:** Containers have ephemeral filesystems. Hardcoded paths may not exist or be writable.
**GCP Services:** Cloud Storage, GCS FUSE, Filestore

## 2. Local File System Dependencies
**What to look for:** Direct file I/O operations (open, read, write) to local disk for persistent data.
**Why it matters:** Container storage is ephemeral. Data is lost on restart.
**GCP Services:** Cloud Storage, Persistent Disk, Filestore

## 3. Hardcoded Ports/IP Addresses
**What to look for:** `localhost`, `127.0.0.1`, hardcoded port numbers like `:8080`, `:5432`, `:3306`
**Why it matters:** In containers, services communicate via service discovery, not fixed IPs/ports.
**GCP Services:** Cloud DNS, Service Mesh (Istio), GKE Service Discovery

## 4. Session State Management (Sticky Sessions)
**What to look for:** In-memory session storage, `HttpSession`, server-side session objects.
**Why it matters:** Container instances are stateless and can be replaced anytime.
**GCP Services:** Memorystore (Redis), Cloud Firestore, Cloud SQL

## 5. Environment-Specific Configurations
**What to look for:** Hardcoded environment names (`production`, `staging`), environment-specific URLs.
**Why it matters:** Containers should be environment-agnostic, configured via env vars.
**GCP Services:** GKE ConfigMaps, Secret Manager, Cloud Run env vars

## 6. Database Connection Handling
**What to look for:** Hardcoded DB connection strings, direct IP-based DB connections.
**Why it matters:** DB connections in containers should use service discovery or proxies.
**GCP Services:** Cloud SQL Proxy, AlloyDB, Cloud Spanner, Connection pooling

## 7. Logging to Local Files
**What to look for:** File-based logging (log4j file appenders, Python file handlers, writing to `/var/log/`).
**Why it matters:** Container logs should go to stdout/stderr for aggregation.
**GCP Services:** Cloud Logging, Cloud Monitoring, stdout/stderr

## 8. Process-Level Dependencies
**What to look for:** Spawning child processes, relying on system services (cron, systemd), PID files.
**Why it matters:** Containers should run a single process. System services aren't available.
**GCP Services:** Cloud Scheduler, Cloud Tasks, Cloud Pub/Sub

## 9. OS-Specific System Calls
**What to look for:** Windows API calls, Linux-specific syscalls, platform-dependent libraries.
**Why it matters:** Container base images may differ from development OS.
**GCP Services:** Use multi-stage builds, distroless images

## 10. Large Binary Dependencies
**What to look for:** Large native libraries, embedded binary assets, ML models bundled in code.
**Why it matters:** Increases image size, slows deployments, wastes resources.
**GCP Services:** Artifact Registry, Cloud Storage for assets, Vertex AI for models

## 11. Hardcoded Secrets/Credentials
**What to look for:** API keys, passwords, tokens embedded in source code or config files.
**Why it matters:** Security risk. Secrets should be injected at runtime.
**GCP Services:** Secret Manager, Workload Identity, GKE Secrets

## 12. Shared Memory / IPC Dependencies
**What to look for:** Shared memory segments, named pipes, Unix domain sockets, mmap.
**Why it matters:** Containers are isolated. IPC between containers requires explicit setup.
**GCP Services:** Cloud Pub/Sub, Cloud Tasks, gRPC

## 13. Startup/Shutdown Scripts
**What to look for:** init.d scripts, systemd units, custom startup scripts depending on host.
**Why it matters:** Containers use ENTRYPOINT/CMD. Lifecycle management differs.
**GCP Services:** GKE init containers, Cloud Run startup probes

## 14. Host-Dependent Networking
**What to look for:** Binding to specific network interfaces, host networking, iptables rules.
**Why it matters:** Container networking is virtualized. Host network access is restricted.
**GCP Services:** GKE VPC-native networking, Cloud NAT, Cloud Load Balancing

## 15. Persistent Local Storage Usage
**What to look for:** SQLite databases, local caches written to disk, temp files used across requests.
**Why it matters:** Local storage doesn't persist across container restarts or scaling.
**GCP Services:** Cloud SQL, Memorystore, Cloud Storage, Persistent Volumes
