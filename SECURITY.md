# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please DO NOT report it by opening a public GitHub issue. 

Instead, please send an email directly to the maintainer. We will prioritize reviewing and addressing the report immediately.

## Scope of Support

We only provide security updates for the latest major version of this project.

## Privacy and Network Boundaries

This tool acts as a local proxy circuit breaker. By design:
* **Network Binding**: The native Python CLI binds exclusively to `127.0.0.1` (loopback) by default. This prevents unauthorized access from other machines on your network. DO NOT expose this proxy to the public internet.
* **Data Storage**: Local usage and budget metadata are stored locally on your machine in a SQLite database (`data/budget.db`). 
* **Data Transmission**: This proxy does not send telemetry, analytics, or user data to any external service. Your request payloads and API keys are forwarded *only* to the upstream provider you have configured (e.g., OpenAI).
