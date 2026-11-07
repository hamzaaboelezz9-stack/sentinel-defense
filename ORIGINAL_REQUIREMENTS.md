# MASTER CODEX PROMPT — BUILD SENTINEL DEFENSE: COMPLETE 8-WEEK ENGINEERING PROJECT

## YOUR ROLE

Act simultaneously as a Principal Cybersecurity Engineer, Security Operations Center (SOC) Architect, Senior Full-Stack Software Engineer, Machine Learning Engineer, DevSecOps Engineer, UI/UX Designer, QA Automation Engineer, and Engineering Technical Lead.

You are responsible for delivering a complete, integrated, highly professional defensive cybersecurity engineering project called:

**SENTINEL DEFENSE — Intelligent Cyber Defense & Critical Infrastructure Security Operations Platform**

**Mission:** Create an impressive, technically credible cybersecurity system suitable for a student to demonstrate in a Military Technical College (MTC), Egypt, engineering portfolio presentation.

This is a defensive, educational security engineering project. Its realistic interface, engineering rigor, reliability, and demonstrations should impress experienced technical evaluators.

Do not claim the project is officially approved by, affiliated with, certified by, or operationally deployed for any military organization. It must remain a safe simulated platform, not a live military system.

---

# 1. CRITICAL INSTRUCTIONS

I have previously built SENTINEL DEFENSE through Week 5, including:

- Week 1: FastAPI backend, event ingestion, SQLite, introductory detection, pytest.
- Week 2: Correlation rules, brute-force detection, password spraying, disabled-account alerts, deduplication.
- Week 3: SOC dashboard, incident investigations, timelines, analytics, evidence, reports.
- Week 4: Persistence, FastAPI integration, SQLite, application security, offline browser mode.
- Week 5: Explainable statistical anomaly detection, synthetic training datasets, anomaly scores, confusion matrix, performance comparisons.

**FIRST:** Examine all files available in the current workspace, including any uploaded Week 5 ZIP or repository.

**SECOND:** Preserve working functionality and improve existing code wherever possible. Do not unnecessarily replace reliable modules. Identify and correct architectural weaknesses.

**THIRD:** Complete and integrate all eight project weeks into ONE coherent final application. Do not deliver eight unrelated demonstrations.

**FOURTH:** Implement actual functioning software. No fake buttons, decorative-only dashboards, hardcoded success metrics represented as live results, fabricated API responses, or unimplemented features marketed as complete.

**FIFTH:** Work through all development stages autonomously. Do not stop after planning or creating a README. Create files, install dependencies where permitted, run tests, fix failures, and validate functionality.

If the existing project is unavailable, initialize a new repository and implement the requirements from the beginning.

If a tool, dependency, browser, or test environment is unavailable, document exactly what could not be validated. Never claim to have executed tests you did not run.

Make sensible engineering decisions without asking unnecessary questions.

---

# 2. PROJECT VISION

Imagine a secure Security Operations Center used to train engineers to protect a simulated critical infrastructure organization.

The fictional environment contains:

- Headquarters IT network
- Operations workstations
- Application servers
- Identity and authentication services
- Database servers
- Network infrastructure devices
- Industrial monitoring simulators
- Security administration workstations

All devices, users, security events, and IP addresses must be fictional.

Use reserved documentation IP address ranges, such as 192.0.2.0/24, 198.51.100.0/24, and 203.0.113.0/24.

The application should provide:

1. Real-time simulated situational awareness.
2. Intelligent security event analysis.
3. Threat detection and correlation.
4. Explainable machine learning.
5. Incident investigation and management.
6. Decision-support and defensive response recommendations.
7. Evidence preservation and audit histories.
8. Professional incident and executive reports.
9. System health and reliability monitoring.
10. A polished demonstration mode suitable for technical presentations.

The software must not scan external networks, compromise systems, generate real attacks, interact with operational military equipment, or perform automatic network disruption.

---

# 3. TECHNOLOGY STACK

Use the following preferred architecture unless an alternative is clearly justified.

### Backend
- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2
- Alembic database migrations
- SQLite for simple local installation
- PostgreSQL support for the advanced deployment
- Uvicorn
- Structured application logging

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- Professional UI component system
- Recharts or a comparable charting library
- React Router
- Accessible, responsive components

### Artificial Intelligence
- Python
- NumPy
- pandas
- scikit-learn
- Explainable statistical anomaly scoring
- Isolation Forest as an optional comparison model
- Reproducible synthetic datasets

### Security and Quality
- pytest
- pytest-cov
- Ruff
- mypy where practical
- Vitest
- Playwright end-to-end tests
- GitHub Actions
- Dependency vulnerability scanning
- Docker and Docker Compose
- Environment-based configuration

### Reporting
- Professional PDF generation
- CSV export
- JSON export
- Evidence and incident summaries

### Deployment
Provide both:

**MODE A — EASY DEMO:** A standalone browser-accessible demonstration that works without installing Python, preserving its own fictional data in local browser storage. It must be clearly labeled as a simulation.

**MODE B — CONNECTED PROFESSIONAL APPLICATION:** A complete React frontend connected to FastAPI, with persistent SQLite/PostgreSQL storage, authentication, and all integrated engineering features.

The demo and connected modes should share documented data schemas and consistent detection behavior as far as practical.

---

# 4. COMPLETE EIGHT-WEEK DEVELOPMENT REQUIREMENTS

## WEEK 1 — SOFTWARE ARCHITECTURE AND FOUNDATION

Build or improve:

- Clean modular project structure.
- Documented system architecture.
- FastAPI application.
- API versioning using `/api/v1`.
- Pydantic event models.
- Strong request validation.
- SQLite persistence.
- Synthetic security event generator.
- Health and readiness endpoints.
- OpenAPI documentation.
- Typed configuration.
- Structured error responses.
- Automated unit tests.

Define a consistent security event format containing:

- Unique event ID
- Timestamp in UTC
- Device ID
- Source IP
- Destination IP where appropriate
- Username
- Event category
- Event type
- Status
- Severity
- Synthetic environment identifier
- Related incident ID
- Ground-truth label where available for evaluations

Implement safe handling of invalid timestamps, duplicate event IDs, missing fields, and malformed records.

**Deliverable:** Working, tested event ingestion and storage service.

## WEEK 2 — SECURITY DETECTION AND CORRELATION ENGINE

Implement or improve these defensive detection rules:

1. Brute force: five or more failed login attempts from one source IP within 60 seconds.
2. Password spraying: failed attempts targeting at least five distinct accounts within 120 seconds.
3. Disabled-account access: successful authentication to a disabled account.
4. Unusual login time: authentication outside configurable working hours.
5. Excessive authentication failures: abnormal failure ratios.
6. Suspicious repeated access: repeated access-denied events in fictional logs.
7. Unexpected device configuration change: synthetic configuration-change events.
8. Synthetic device health anomaly: unusual telemetry from a simulated device.

Implement:

- Configurable thresholds.
- Sliding time windows.
- Stateful incident correlation.
- Incident deduplication.
- Alert cooldown policies.
- Event-to-alert evidence references.
- Alert severity classification.
- Rule version metadata.
- Late-arriving event handling.
- Idempotent processing.
- Meaningful detection explanations.
- False-positive test scenarios.

Ensure unrelated IP addresses and usernames are not incorrectly grouped into the same incident.

**Deliverable:** Reliable, testable correlation engine.

## WEEK 3 — ADVANCED SECURITY OPERATIONS DASHBOARD

Create a polished Security Operations Center interface.

The dashboard must include:

### Executive Overview
- Total security events
- Active incidents
- Critical incidents
- Monitored simulated assets
- Detection trends
- Incident severity distribution
- Investigation workload
- Time to acknowledge and resolve incidents
- System health

### Security Monitoring
- Live simulated event stream
- Search and filtering
- Severity indicators
- Time-range controls
- Device monitoring table
- Event category charts
- Alert activity timeline

### Incident Investigation
- Searchable incident list
- Detailed incident view
- Supporting evidence
- Event timeline
- Analyst notes
- Incident assignment
- Severity and status management
- Incident history
- False-positive and confirmed-incident classifications

### Network Visualization
Build a visually appealing interactive topology of the fictional organization's network.

Include device relationships, device health, simulated security events, and visual incident indicators.

All visualization data must correspond to actual simulated records, not decorative values.

### UI Design Requirements
The interface should feel like sophisticated enterprise cybersecurity software:

- Dark navy security operations theme
- Elegant typography
- Cyan accents for informational data
- Amber and red for real severity distinctions
- Responsive desktop and laptop layouts
- Functional mobile layouts
- Smooth, purposeful transitions
- Accessible keyboard interaction
- Loading, empty, and error states
- Light/dark theme if practical
- English/Arabic language switching if practical, including correct RTL support

Do not use official Egyptian military logos or imply institutional endorsement.

**Deliverable:** Functional, visually outstanding SOC dashboard.

## WEEK 4 — DATABASE, AUTHENTICATION, AND SECURITY HARDENING

Connect the dashboard to the persistent FastAPI backend.

Implement:

- Database relationships between events, assets, incidents, evidence, users, and notes.
- Database migrations.
- Authentication.
- Password hashing using Argon2 or another established modern password-hashing implementation.
- Role-based authorization.

Roles:

- Administrator
- Security Analyst
- Read-Only Viewer

Implement proper restrictions for every API endpoint, not just frontend navigation.

Add:

- Secure session or token handling.
- Reasonable request rate limits.
- Strict input validation.
- Restricted CORS.
- Secret configuration through environment variables.
- No secrets committed to Git.
- Safe error messages.
- Audit logs for important changes.
- Export restrictions based on role.
- Basic security headers.
- Safe handling of user-generated notes.
- Reasonable data retention controls.
- Backup and restore procedures for the local database.

Provide demo accounts only in development/demo mode and clearly label them.

Bind local servers to localhost by default. Do not expose the application publicly by default.

Include tests for authentication failures, unauthorized access, permission enforcement, injection attempts, and corrupted input.

**Deliverable:** Persistent, access-controlled application ready for a controlled demonstration.

## WEEK 5 — EXPLAINABLE AI ANOMALY DETECTION

Preserve and strengthen existing Week 5 work.

Create a reproducible synthetic dataset pipeline.

Keep separate datasets for:

1. Model training
2. Threshold calibration
3. Held-out evaluation

Prevent training/test leakage.

Build anomaly detection using measurable characteristics such as:

- Failed-login frequency
- Failure ratio
- Unique account targets
- Login time deviation
- Device activity deviation
- Event frequency
- Disabled-account indicators

Include:

- A transparent statistical baseline.
- Optional Isolation Forest implementation.
- Anomaly scores.
- Configurable sensitivity.
- Feature-level explanations where technically valid.
- Separate rule-based and model-based results.
- Precision, recall, F1, specificity, and false-positive rate.
- Confusion matrix.
- ROC or precision-recall analysis where appropriate.
- Threshold comparisons.
- Saved model metadata.
- Reproducible random seeds.
- Model limitation documentation.

Evaluate the model using actual held-out synthetic labels, not manually invented accuracy percentages.

Never equate anomaly detection with proof of malicious activity.

Clearly indicate that the model is experimental and not validated on real operational networks.

**Deliverable:** Explainable, reproducible AI Detection Laboratory integrated with the dashboard.

## WEEK 6 — INTELLIGENT INCIDENT RESPONSE ASSISTANT

Build an incident response assistant that helps human operators investigate synthetic threats.

For each incident, provide:

- Human-readable incident summary.
- Detection explanation.
- Supporting evidence.
- Confidence or uncertainty indicators where justified.
- Possible benign explanations.
- Recommended investigation steps.
- Suggested defensive containment actions.
- Impact considerations.
- Recovery checklist.
- Verification checklist.
- Incident closure recommendations.

Implement safe response playbooks for:

- Brute-force authentication activity.
- Password spraying.
- Disabled-account login.
- Suspicious configuration changes.
- Unusual login activity.
- Simulated endpoint health anomalies.
- Simulated network device anomalies.

The assistant should work offline using deterministic, auditable playbook rules.

An optional language-model integration may be included behind an explicit configuration flag, but the default must function without external API keys.

Prevent AI-generated text from directly executing commands or altering infrastructure.

All disruptive actions require human approval, and the demo must not implement real network blocking or account disabling.

Include analyst decision history and audit trails.

**Deliverable:** A working, explainable, human-supervised incident response assistant.

## WEEK 7 — PROFESSIONAL REPORTING AND EVIDENCE MANAGEMENT

Build a professional reporting center with:

### Incident Reports
- Incident identification
- Severity
- Detection method
- Time of occurrence
- Affected fictional assets
- Event timeline
- Evidence summary
- Analyst findings
- Recommended mitigations
- Incident status
- Limitations and confidence

### Executive Security Briefing
Create a leadership-level report explaining:

- Overall simulated security posture
- Number of incidents
- Most important trends
- High-priority risks
- System readiness
- Recommended improvements
- Relevant operational considerations
- Engineering limitations

### Technical Performance Report
Include:

- Detection rule coverage
- Alert volumes
- False-positive statistics
- Model performance
- Event-processing performance
- Application reliability
- Test results
- Known issues
- Engineering improvements

### Export Capabilities
Provide working exports to:

- PDF
- JSON
- CSV

Use real project data for every displayed result. Label simulated results appropriately.

Include report timestamps, schema versions, and sufficient evidence identifiers for reproducibility.

**Deliverable:** Professional incident and executive reports suitable for a technical project demonstration.

## WEEK 8 — FINAL ENGINEERING VALIDATION, DEPLOYMENT, AND PRESENTATION

Complete the integrated final release.

### Reliability and Performance
- Test large synthetic event batches.
- Measure ingestion throughput.
- Measure query latency.
- Test duplicate event behavior.
- Test application restarts.
- Test database persistence.
- Test malformed events.
- Test alert deduplication.
- Test concurrency where appropriate.
- Measure performance rather than inventing benchmark numbers.

### Quality Assurance
- Backend unit tests.
- Backend integration tests.
- Frontend component tests.
- End-to-end browser tests.
- Authentication and authorization tests.
- Detection accuracy tests.
- Database migration tests.
- Report generation tests.
- Regression tests for Weeks 1–7.

Use CI to run relevant tests automatically.

### Developer Experience
Provide:

- `README.md`
- `ARCHITECTURE.md`
- `SECURITY.md`
- `THREAT_MODEL.md`
- `API_REFERENCE.md`
- `TESTING.md`
- `DEPLOYMENT.md`
- `LIMITATIONS.md`
- `PROJECT_PRESENTATION.md`
- `CHANGELOG.md`
- `.env.example`
- `LICENSE`
- Clean `.gitignore`

### Installation and Launch
Create:

1. A simple `START_SENTINEL_DEFENSE_WINDOWS.bat` launcher.
2. A Docker Compose option.
3. A development-mode setup guide.
4. A standalone offline browser demonstration.
5. A production-like local deployment configuration.
6. A clear troubleshooting guide for Python not found, PowerShell restrictions, dependency errors, and port conflicts.

The Windows launcher must not depend on activating PowerShell scripts. It should detect Python, provide useful errors, create its environment, install dependencies when necessary, and launch the application.

### GitHub Release
Prepare the repository with:

- Professional project description.
- Excellent README.
- Architecture diagrams.
- Screenshots.
- Demonstration instructions.
- Test badges only when backed by actual CI.
- Meaningful version information.
- Initial release notes.
- Reproducible dataset generation instructions.

**Deliverable:** SENTINEL DEFENSE v1.0 — a complete, integrated defensive cybersecurity engineering portfolio application.

---

# 5. SPECIAL FEATURE — MTC ENGINEERING PRESENTATION MODE

This is particularly important.

Create a dedicated **Engineering Demonstration Mode** designed for presenting this project to technically experienced evaluators.

This is not a military-command interface and should not imply actual military use.

It should present a controlled fictional scenario in approximately seven minutes.

### Demonstration Sequence

**Stage 1 — System Overview**

Show the simulated organization's network, protected assets, and normal event activity.

**Stage 2 — Simulated Security Incident**

Generate an entirely fictional authentication incident and show how events enter the detection pipeline.

**Stage 3 — Detection**

Demonstrate the relevant rule, the alert threshold, and the resulting incident.

**Stage 4 — AI Analysis**

Display anomaly scores, important features, and the difference between rule-based and model-based predictions.

**Stage 5 — Investigation**

Show event evidence, incident timeline, classification, and analyst notes.

**Stage 6 — Human-Supervised Response**

Show a recommended response playbook and explain why the system does not automatically perform disruptive actions.

**Stage 7 — Final Report**

Generate a professional PDF briefing that summarizes the case, system performance, findings, and engineering limitations.

Provide a button to reset the entire demonstration to a known reproducible state.

Include an optional presenter narrative explaining each stage in simple technical English.

### Engineering Knowledge Panel

Add a page explaining:

- Why FastAPI was selected.
- Why relational storage was selected.
- How event correlation works.
- Why deduplication matters.
- Why machine learning can generate false alarms.
- How role-based access control protects the system.
- What automated tests establish.
- What limitations remain.
- What would be required before any real operational deployment.

The goal is to demonstrate that I understand the engineering, not simply that I generated code.

---

# 6. FINAL VISUAL QUALITY

Make the system visually exceptional, but credible.

Design direction:

**Premium enterprise cybersecurity operations dashboard.**

Think:

- High-quality security analytics software.
- Clear visual hierarchy.
- Well-designed cards and charts.
- Accurate time-series displays.
- Useful information density.
- Excellent readability.
- Professional severity indicators.
- Strong usability.
- Technical sophistication without unnecessary animations.

Create an original visual identity and logo for SENTINEL DEFENSE using ordinary SVG or CSS assets.

Use the title:

**SENTINEL DEFENSE**

Subtitle:

*Intelligent Cyber Defense & Security Operations Platform*

Add a visible label:

*Defensive Engineering Demonstration — Synthetic Data Only*

Every important UI button must function. No placeholder functionality should be represented as completed.

---

# 7. ENGINEERING REQUIREMENTS

Follow these principles:

**Correctness before appearance.**

**Working software before elaborate documentation.**

**Reproducibility before impressive numbers.**

**Security before convenience.**

**Explainability before black-box predictions.**

**Maintainability before unnecessary complexity.**

**Real test results before marketing claims.**

Use clear functions, types, modules, error handling, and meaningful comments.

Avoid unnecessary microservices. A well-designed modular monolith is preferable for this project.

Keep the application easy enough for an individual student to understand, operate, debug, and demonstrate.

Treat all simulated data and imported records as untrusted input.

Do not implement offensive exploitation, credential theft, stealth mechanisms, destructive functions, or automated actions against real systems.

---

# 8. ACCEPTANCE CRITERIA

Do not declare the final project complete until the following are verified, or their limitations explicitly documented:

- The browser demo opens successfully.
- The connected dashboard launches locally.
- FastAPI endpoints work.
- Events persist after restart.
- Synthetic incident generation works.
- Brute-force detection works.
- Password-spray detection works.
- Duplicate incident suppression works.
- Unauthorized API requests are rejected.
- Role permissions work.
- Investigations can be saved.
- Incident histories remain intact.
- AI anomaly evaluation uses actual generated datasets.
- Model performance metrics are reproducible.
- Response playbooks display correctly.
- PDF report generation works.
- CSV and JSON exports work.
- Demo reset works.
- Frontend/backend integration works.
- Automated tests run successfully.
- The project can be understood and operated using its README.

Include a final acceptance checklist with PASS, FAIL, or NOT TESTED for each criterion.

Do not invent a successful test result when execution was not possible.

---

# 9. REQUIRED FINAL FILE STRUCTURE

Use a clean structure similar to:

```text
SENTINEL-DEFENSE/
|
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |-- core/
|   |   |-- database/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- detection/
|   |   |-- ml/
|   |   |-- incidents/
|   |   |-- response/
|   |   |-- reporting/
|   |   |-- services/
|   |   |-- main.py
|   |
|   |-- alembic/
|   |-- tests/
|   |-- requirements.txt
|
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |-- pages/
|   |   |-- hooks/
|   |   |-- services/
|   |   |-- types/
|   |   |-- styles/
|   |-- package.json
|
|-- demo/
|   |-- index.html
|
|-- datasets/
|   |-- generators/
|   |-- synthetic/
|   |-- evaluations/
|
|-- scripts/
|-- docs/
|-- reports/
|-- tests/
|-- .github/workflows/
|-- docker-compose.yml
|-- .env.example
|-- START_SENTINEL_DEFENSE_WINDOWS.bat
|-- README.md
|-- SECURITY.md
|-- ARCHITECTURE.md
|-- PROJECT_PRESENTATION.md
|-- LICENSE
```

Improve this structure if there is a compelling engineering reason.

---

# 10. FINAL OUTPUT EXPECTATIONS

At the end of implementation, provide:

1. The complete working source code in the workspace.
2. The runnable standalone browser demonstration.
3. The connected FastAPI/React application.
4. The complete synthetic dataset generation pipeline.
5. The automated test suite and actual results.
6. The one-click Windows launcher.
7. Docker deployment files.
8. The engineering documentation.
9. A professional GitHub-ready README.
10. A demonstration walkthrough suitable for MTC engineering evaluators.
11. A list of genuine project limitations.
12. A concise explanation of the five most impressive engineering achievements.
13. An ordered list of commands to run and verify the system.
14. A final ZIP archive if artifact generation is supported.

### Work Execution Instructions

Start by inspecting the existing repository. Write an internal execution plan covering all eight development stages, then implement them sequentially.

Continue implementation through Week 8 within the available execution environment and tool limits.

After every stage, run appropriate tests and correct defects before moving forward.

Do not present architectural diagrams or sample snippets as a substitute for implementing the project.

If execution limits prevent completing everything in one session, preserve all implemented files and provide an exact continuation checklist identifying finished components, incomplete components, and the next implementation action.

**BEGIN BUILDING SENTINEL DEFENSE v1.0 NOW.**

Build the best technically credible, professional, impressive defensive cybersecurity engineering project possible, and make sure its creator can genuinely understand, demonstrate, and defend the engineering decisions during a Military Technical College interview.