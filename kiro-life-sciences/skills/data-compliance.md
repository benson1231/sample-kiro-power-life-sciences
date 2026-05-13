---
inclusion: manual
---

# Data Compliance for Life Sciences

Guidance on regulatory compliance, data protection, and standards for life sciences data.

## HIPAA (Health Insurance Portability and Accountability Act)

### Key Requirements
- Applies to Protected Health Information (PHI) in the United States.
- Requires administrative, physical, and technical safeguards for PHI.
- Minimum Necessary Rule: access only the minimum PHI needed for a task.

### De-identification Methods
- **Safe Harbor**: Remove 18 specific identifiers (names, dates, geographic data, SSN, etc.).
- **Expert Determination**: A qualified statistician certifies re-identification risk is very small.

### Practical Steps
- Never store PHI in version control or unencrypted storage.
- Use AWS services with BAA (Business Associate Agreement) in place.
- Encrypt data at rest (AES-256) and in transit (TLS 1.2+).
- Implement role-based access control for all PHI access.

## GDPR (General Data Protection Regulation)

### Key Principles
- **Lawful basis**: Consent, legitimate interest, or legal obligation.
- **Data minimization**: Collect only what is necessary.
- **Right to erasure**: Data subjects can request deletion.
- **Data portability**: Provide data in machine-readable format on request.

### Genomic Data Considerations
- Genomic data is considered "special category" data under GDPR Article 9.
- Requires explicit consent for processing.
- Pseudonymization is recommended but does not exempt from GDPR.
- Cross-border transfers require Standard Contractual Clauses or adequacy decisions.

## GxP (Good Practice) Regulations

### GLP (Good Laboratory Practice)
- Applies to non-clinical safety studies.
- Requires documented SOPs, audit trails, and data integrity controls.
- All raw data must be retained and traceable.

### GCP (Good Clinical Practice)
- Applies to clinical trials.
- Requires informed consent, IRB/ethics approval, and adverse event reporting.
- Electronic records must comply with 21 CFR Part 11 (FDA) or Annex 11 (EU).

### Data Integrity (ALCOA+)
- **A**ttributable, **L**egible, **C**ontemporaneous, **O**riginal, **A**ccurate.
- Plus: Complete, Consistent, Enduring, Available.

## MIAME and MINSEQE Standards

### MIAME (Minimum Information About a Microarray Experiment)
- Required for ArrayExpress/GEO submissions.
- Must include: experimental design, array design, samples, hybridizations, measurements, normalization.

### MINSEQE (Minimum Information about a high-throughput Nucleotide Sequencing Experiment)
- Required for sequencing experiment submissions.
- Must include: experimental design, sequence read data, quality scores, processing pipeline, processed data.

## Consent Management

### Best Practices
- Use tiered consent models: primary use, secondary research, broad consent.
- Track consent status per sample and per data type.
- Implement consent withdrawal workflows that propagate to all downstream data.
- Use GA4GH Data Use Ontology (DUO) codes for machine-readable consent terms.

## Audit Trails

### Implementation
- Log all data access events with timestamp, user, action, and resource.
- Log all data modifications with before/after values.
- Store audit logs in append-only, tamper-evident storage.
- Retain audit logs for the required period (typically 7–15 years for clinical data).

```python
# Example audit log entry
audit_entry = {
    "timestamp": "2024-01-15T10:30:00Z",
    "user": "researcher@org.com",
    "action": "data_access",
    "resource": "sample_001_wgs",
    "justification": "variant_analysis_project_123"
}
```

## Data Classification

| Level | Description | Examples | Controls |
|-------|-------------|----------|----------|
| Public | Freely available | Reference genomes, published variants | Standard access |
| Internal | Organization use | Aggregated statistics, de-identified data | Authentication required |
| Confidential | Restricted access | Individual-level genomic data | Encryption + RBAC |
| Regulated | Legal requirements | PHI, clinical trial data | Full compliance controls |
