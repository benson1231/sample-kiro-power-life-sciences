---
inclusion: manual
---

# Clinical Interoperability

Practical guidance for working with healthcare data standards: FHIR, HL7 v2, OMOP CDM, and clinical terminologies.

## FHIR (Fast Healthcare Interoperability Resources)

### Core Concepts
- FHIR organizes clinical data into **Resources** (Patient, Observation, Condition, MedicationRequest, etc.).
- Resources are identified by type and ID: `Patient/12345`.
- Use **Bundles** for batch operations and transaction sets.

### Common Resource Types
- **Patient**: Demographics, identifiers, contact information.
- **Observation**: Lab results, vital signs, genomic variants.
- **Condition**: Diagnoses, problems, health concerns.
- **DiagnosticReport**: Genomic test results, pathology reports.
- **MolecularSequence**: Genomic sequence data with variant annotations.

### FHIR Search
```
GET /Patient?name=Smith&birthdate=1990-01-01
GET /Observation?patient=12345&code=http://loinc.org|718-7
GET /Condition?patient=12345&category=genomic
```

### Genomics in FHIR
- Use the FHIR Genomics Implementation Guide for variant reporting.
- Map VCF fields to `Observation` resources with `component` elements.
- Link genomic findings to `DiagnosticReport` for clinical context.

## HL7 v2 Messaging

### Message Structure
- Messages are pipe-delimited with segments (MSH, PID, OBR, OBX).
- Each segment starts with a 3-character identifier.
- Fields are separated by `|`, components by `^`, sub-components by `&`.

### Common Message Types
- **ADT (Admit/Discharge/Transfer)**: Patient movement events.
- **ORM/OML**: Order messages for lab tests.
- **ORU**: Observation results (lab results, genomic reports).

### Example ORU Message
```
MSH|^~\&|LAB|HOSPITAL|EHR|HOSPITAL|20240115||ORU^R01|MSG001|P|2.5.1
PID|1||12345^^^HOSP||DOE^JOHN||19900101|M
OBR|1||ORD001|81479^Genomic Sequencing^CPT
OBX|1|ST|81247-9^BRCA1 gene^LN||Pathogenic variant detected||||||F
```

### Parsing Tips
- Always validate the MSH segment first for encoding characters.
- Handle optional segments gracefully — not all messages include all segments.
- Use the HL7 v2 tools in the healthcare MCP server for parse/generate operations.

## OMOP CDM (Common Data Model)

### Key Tables
- **PERSON**: Patient demographics.
- **CONDITION_OCCURRENCE**: Diagnoses with start/end dates.
- **DRUG_EXPOSURE**: Medication prescriptions and administrations.
- **MEASUREMENT**: Lab results, vital signs, genomic measurements.
- **OBSERVATION**: Clinical observations not fitting other tables.

### Mapping Workflow
1. Extract source data (EHR, claims, registry).
2. Map source codes to OMOP standard concepts using Athena vocabulary.
3. Load into CDM tables with proper foreign key relationships.
4. Validate with OHDSI Data Quality Dashboard.

### FHIR to OMOP Mapping
| FHIR Resource | OMOP Table | Key Fields |
|---------------|------------|------------|
| Patient | PERSON | gender, birth_date, race |
| Condition | CONDITION_OCCURRENCE | condition_concept_id, start_date |
| MedicationRequest | DRUG_EXPOSURE | drug_concept_id, start_date |
| Observation (lab) | MEASUREMENT | measurement_concept_id, value |

## Clinical Terminologies

### SNOMED CT
- Comprehensive clinical terminology with hierarchical concepts.
- Use for diagnoses, procedures, findings, and body structures.
- Concept IDs are numeric (e.g., `73211009` for diabetes mellitus).

### LOINC (Logical Observation Identifiers Names and Codes)
- Standard for lab tests and clinical observations.
- Use for ordering and reporting lab results.
- Codes follow pattern: `718-7` (Hemoglobin), `81247-9` (BRCA1 variant).

### ICD-10 (International Classification of Diseases)
- Used for billing, epidemiology, and mortality statistics.
- Codes follow pattern: `C50.9` (breast cancer), `E11` (type 2 diabetes).

### Terminology Services
- Use the ontologies MCP server to look up and validate codes.
- Cross-reference between terminologies using concept maps.
- Always include the code system URI when exchanging coded data.

```json
{
  "coding": [{
    "system": "http://snomed.info/sct",
    "code": "73211009",
    "display": "Diabetes mellitus"
  }]
}
```
