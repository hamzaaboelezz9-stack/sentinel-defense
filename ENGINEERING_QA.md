# Engineering questions to practice
**Why FastAPI?** Pydantic contracts reject malformed events, dependency injection places role checks at the API boundary, and OpenAPI makes the contract reviewable.

**Why relational storage?** Investigations need durable relationships between exact events, incidents, evidence, operators, and notes. Foreign keys prevent dangling references, while transactions make duplicate/conflict behavior predictable.

**How do late events work?** Events are ordered by their timestamps within each affected source/asset history. Sliding windows are replayed; overlapping evidence reconciles existing incidents. If a late sequence bridges two episodes, both analyst histories survive in one case and the merge is audited.

**Why not call the model “accurate against attacks”?** Labels come from synthetic scenario construction. Training, calibration and held-out windows are independent, but the distribution is engineered. These metrics test reproducibility under that distribution, not operational detection performance.

**What do feature contributions mean?** The statistical baseline calculates positive standardized deviations from normal training means, divided by the number of features. Their sum is the score. This is an exact decomposition of this baseline, not an explanation of Isolation Forest internals.

**Why keep rules and ML separate?** Rules expose thresholds and concrete evidence; the model identifies statistical deviation. They can disagree. Neither proves intent, so the analyst records classification and benign alternatives.

**Can the assistant block a source?** No. It displays deterministic, versioned advice. The platform has no implementation that blocks networks, disables accounts, scans targets, or executes generated commands.

**Are the hashes a complete forensic chain?** No. They identify local modification and link audit records, but a privileged administrator could rewrite an entire local chain. External custody and independent timestamps would be needed for stronger assurances.

**What do the tests establish?** Specific reproducible behaviors: validation, RBAC, conflict rollback, correlation, migration, persistence, reports, model provenance, browser parity and local deployment. They do not establish universal security or real-world reliability.

**What was difficult?** Preserving analyst notes through deduplication and schema migration, keeping event-time logic consistent between Python and TypeScript, measuring rather than inventing performance, and distinguishing browser-demo convenience from connected API security.
