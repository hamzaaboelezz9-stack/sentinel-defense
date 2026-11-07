# Reproducible synthetic data
Generate with `python scripts/generate_dataset.py`. Seeds 42/43/44 produce independent training (800), calibration (300) and evaluation (500) event windows. Raw windows and labels are in synthetic/*.events.json; feature matrices and labels are in the corresponding CSV files.

Features are extracted from each window: authentication failure count, authentication failure ratio, distinct failed-account targets, off-hours event ratio, telemetry peak, total event count, and successful-disabled-account count. Ground-truth labels never enter this extraction function. Labeled normal windows from the training split fit the baseline and Isolation Forest. Calibration labels choose thresholds. Held-out labels are used only for evaluation.

Anomalous scenarios include concentrated failures, spraying, disabled-account indicators and elevated telemetry; normal scenarios include occasional failures and off-hours activity to expose false positives. These intentionally simplified distributions are not operational threat intelligence. Overlap between benign and suspicious patterns is expected.

The baseline uses normal training means and standard deviations with feature-specific minimum scales. Contributions are positive standardized deviations divided by seven, so they sum exactly to its score. They do not explain Isolation Forest's internal tree decisions. Threshold sensitivity scales the baseline threshold without retraining. Regenerate browser metadata and parity fixtures before building frontend changes to model logic.
