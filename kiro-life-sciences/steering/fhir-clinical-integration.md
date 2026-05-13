---
inclusion: auto
fileMatchPattern: "**/*fhir*,**/*clinical*,**/*omop*,**/*hl7*"
---

# FHIR Clinical Integration

Step-by-step guide to connect to FHIR servers, query resources, and map to OMOP CDM.

## Step 1: Connect to FHIR Server

1. Configure the FHIR server endpoint:
   - Set `FHIR_BASE_URL` environment variable in mcp.json.
2. Test connectivity:
   - Use `life-sciences-healthcare` → `fhir_query` tool with resource type "CapabilityStatement".
3. Review supported resources and search parameters.

## Step 2: Query Patient Data

1. Search for patients:
   - Use `fhir_query` with resource type "Patient" and search parameters (name, birthdate, identifier).
2. Retrieve patient demographics and identifiers.
3. Use the patient ID for subsequent resource queries.

## Step 3: Retrieve Clinical Observations

1. Query observations for a patient:
   - Use `fhir_query` with resource type "Observation" and `patient` parameter.
2. Filter by LOINC code for specific lab results (e.g., `718-7` for hemoglobin).
3. Retrieve conditions, medications, and diagnostic reports similarly.

## Step 4: Map to OMOP CDM

1. For each FHIR resource, map to the corresponding OMOP table:
   - Patient → PERSON
   - Condition → CONDITION_OCCURRENCE
   - MedicationRequest → DRUG_EXPOSURE
   - Observation (lab) → MEASUREMENT
2. Map terminology codes:
   - SNOMED CT → OMOP standard concept IDs using Athena vocabulary.
   - LOINC → OMOP measurement concept IDs.
   - ICD-10 → OMOP condition concept IDs.
3. Use `life-sciences-healthcare` → `omop_map` tool for automated mapping.

## Step 5: Validate Mapped Data

1. Check for unmapped codes and resolve manually.
2. Verify foreign key relationships between OMOP tables.
3. Run data quality checks on the mapped dataset.

## Expected Outputs
- FHIR resources retrieved and structured.
- OMOP CDM tables populated with mapped clinical data.
- Mapping report with coverage statistics and unmapped codes.
