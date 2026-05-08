# KIRO FOR LIFE SCIENCES — TESTER DEPLOYMENT GUIDE

## WHAT IS THIS?

Kiro for Life Sciences is a comprehensive Power package that turns Kiro into
a full-featured life sciences development environment. It provides:

• 24 modular MCP servers covering 100+ databases, tools, and platforms across
  ALL life sciences disciplines — not just genomics
• 10 domain skills with practical guidance for bioinformatics, clinical data,
  ecology, cheminformatics, imaging, immunology, metabolomics, and more
• 16 guided workflows (steering files) for common multi-step tasks
• A searchable resource catalog with 25 categories
• An onboarding dashboard showing everything available at a glance
• Cross-database search that queries multiple databases simultaneously
• Integration with AWS HealthOmics for running genomics pipelines

The architecture is modular: one central Power acts as the hub, and users
install only the MCP servers they need. Each server is a standalone Python
package runnable via `uvx`.

**Disciplines covered:**

Genomics & Sequencing | Proteomics | Structural Biology | Pathways |
Ontologies | Clinical & Pharma | Model Organisms | Molecular Biology |
Computational Chemistry | Immunology | Microbiology & Metagenomics |
Metabolomics | Epigenomics | Imaging & Microscopy | Agriculture & Plants |
Ecology & Environment | Neuroscience | Cell Biology | Healthcare Standards |
Biobanking | Pipelines | Data Standards | Cloud & HPC | AI/ML

**What you can do with it:**

- Search and query 100+ life sciences databases from within Kiro
- Run bioinformatics pipelines (nf-core, WDL, CWL) via AWS HealthOmics
- Design PCR primers and cloning strategies
- Perform molecular docking and ADMET predictions
- Analyze antibody sequences and predict epitopes
- Submit BLAST searches and multiple sequence alignments
- Validate data standards (SBML, ISA-Tab, MAGE-TAB, BioPAX)
- Exchange clinical data via FHIR, HL7, and OMOP CDM
- Submit compute jobs to AWS Batch, Terra, and Galaxy
- Run protein structure predictions with ESM and AlphaFold
- Extract biomedical entities from text with BioNLP
- Cross-reference gene-disease associations across multiple databases
- And much more...


## PART 1: DEPLOYMENT INSTRUCTIONS

**Prerequisites:**
- Kiro IDE installed
- Python 3.10 or higher
- uv package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Step 1: Unzip the package

Unzip kiro-life-sciences.zip to a location of your choice:

```bash
unzip kiro-life-sciences.zip -d ~/kiro-life-sciences-project
cd ~/kiro-life-sciences-project/KiroLS
```

### Step 2: Create a virtual environment and install packages

```bash
uv venv .venv
source .venv/bin/activate

# Install the shared base package first
uv pip install -e ./life-sciences-common

# Install the central Power package
uv pip install -e "./kiro-life-sciences[dev]"

# Install whichever MCP servers you want to test (pick any/all):
uv pip install -e ./life-sciences-genomics
uv pip install -e ./life-sciences-proteomics
uv pip install -e ./life-sciences-structural
uv pip install -e ./life-sciences-pathways
uv pip install -e ./life-sciences-ontologies
uv pip install -e ./life-sciences-clinical
uv pip install -e ./life-sciences-model-organisms
uv pip install -e ./life-sciences-molbio
uv pip install -e ./life-sciences-cheminformatics
uv pip install -e ./life-sciences-immunology
uv pip install -e ./life-sciences-microbiology
uv pip install -e ./life-sciences-metabolomics
uv pip install -e ./life-sciences-epigenomics
uv pip install -e ./life-sciences-imaging
uv pip install -e ./life-sciences-agriculture
uv pip install -e ./life-sciences-ecology
uv pip install -e ./life-sciences-neuroscience
uv pip install -e ./life-sciences-cellbiology
uv pip install -e ./life-sciences-healthcare
uv pip install -e ./life-sciences-biobanking
uv pip install -e ./life-sciences-pipelines
uv pip install -e ./life-sciences-datastandards
uv pip install -e ./life-sciences-cloud
uv pip install -e ./life-sciences-aiml
```

### Step 3: Copy the Power into Kiro

```bash
cp -r kiro-life-sciences/ ~/.kiro/powers/kiro-life-sciences/
```

This makes the Power available in Kiro's Powers panel with its skills,
steering files, and onboarding dashboard.

### Step 4: Configure MCP servers in your workspace

Create or edit `.kiro/settings/mcp.json` in your Kiro workspace:

```json
{
  "mcpServers": {
    "life-sciences-genomics": {
      "command": "/path/to/KiroLS/.venv/bin/life-sciences-genomics"
    },
    "life-sciences-proteomics": {
      "command": "/path/to/KiroLS/.venv/bin/life-sciences-proteomics"
    },
    "life-sciences-structural": {
      "command": "/path/to/KiroLS/.venv/bin/life-sciences-structural"
    }
  }
}
```

Replace `/path/to/KiroLS/` with the actual path where you unzipped.
Add only the servers you installed in Step 2.

### Step 5: Configure credentials (optional)

For databases that require API keys, add env vars:

```json
{
  "mcpServers": {
    "life-sciences-genomics": {
      "command": "/path/to/KiroLS/.venv/bin/life-sciences-genomics",
      "env": {
        "NCBI_API_KEY": "your-ncbi-api-key-here"
      }
    },
    "life-sciences-clinical": {
      "command": "/path/to/KiroLS/.venv/bin/life-sciences-clinical",
      "env": {
        "OMIM_API_KEY": "your-omim-key",
        "DRUGBANK_API_KEY": "your-drugbank-key"
      }
    }
  }
}
```

### Step 6: Verify installation

Run the test suite to confirm everything works:

```bash
cd ~/kiro-life-sciences-project/KiroLS
source .venv/bin/activate
pytest kiro-life-sciences/tests/ -q
pytest life-sciences-common/tests/ -q
```

Expected: 338+ tests passing for kiro-life-sciences, 32 for life-sciences-common.

### Step 7: Test in Kiro

1. Open Kiro
2. Activate the "kiro-life-sciences" Power from the Powers panel
3. Try asking: "Search NCBI for BRCA1" or "Look up TP53 in UniProt"
4. The Power's tools should be available in chat


## PART 2: PACKAGE CONTENTS

### kiro-life-sciences/ — Central Power Hub

| Component | Description |
|-----------|-------------|
| `POWER.md` | Documentation and getting-started guide |
| `pyproject.toml` | Package config (pydantic, httpx, pytest, hypothesis) |
| `bundle-manifest.json` | Declares all 24 MCP servers, 10 skills, 16 steering files |
| `skills/` | 10 domain-specific skill files |
| `steering/` | 16 step-by-step workflow guides |
| `src/kiro_life_sciences/` | Core Python modules (catalog, dashboard, credentials, installer, skills) |

**Skills:**

| File | Topic |
|------|-------|
| bioinformatics-file-formats.md | FASTA, FASTQ, BAM, VCF, GFF, BED, DICOM, SBML |
| genomics-pipeline-best-practices.md | WDL/Nextflow/CWL design patterns |
| data-compliance.md | HIPAA, GDPR, GxP, MIAME, MINSEQE |
| clinical-interoperability.md | FHIR, HL7, OMOP CDM |
| ecological-data-analysis.md | Species distribution, biodiversity, eDNA |
| cheminformatics-best-practices.md | SMILES, InChI, Lipinski, SAR |
| biomedical-imaging.md | Segmentation, feature extraction, DICOM |
| immunology-vaccine-design.md | Epitope prediction, MHC binding, antibodies |
| metabolomics-analysis.md | Metabolite ID, spectral matching |
| single-cell-analysis.md | QC, clustering, trajectory inference |

**Steering workflows:**

| File | Workflow |
|------|----------|
| variant-calling-pipeline.md | HealthOmics variant calling setup |
| gene-disease-associations.md | ClinVar → OMIM → HPO cross-referencing |
| protein-structure-analysis.md | PDB → AlphaFold → CATH workflows |
| pipeline-import-healthomics.md | Import nf-core/WDL into HealthOmics |
| resource-catalog-browsing.md | How to search/browse the catalog |
| fhir-clinical-integration.md | FHIR + OMOP CDM workflows |
| species-distribution-analysis.md | GBIF → IUCN → iNaturalist |
| metabolite-identification.md | HMDB → MetaboLights → MassBank |
| microbiome-analysis.md | SILVA → QIIME 2 → MG-RAST |
| compound-screening.md | PubChem → RDKit → ZINC → docking |
| biomedical-image-analysis.md | OMERO → CellProfiler → ImageJ |
| molecular-docking.md | PDB → ligand prep → SwissDock |
| primer-design-cloning.md | Primer3 → PrimerBLAST → REBASE |
| single-cell-rnaseq.md | CellxGene → expression analysis |
| epigenomics-analysis.md | IHEC → Roadmap → ENCODE |
| amr-analysis.md | CARD → BV-BRC resistance profiling |

---

### life-sciences-common/ — Shared Base Package

- `BaseLifeSciencesServer` — Async HTTP client with retry logic
- Error classes — RateLimitError, AuthenticationError, NotFoundError, etc.
- Exponential backoff — 429 retry, 5xx retry, timeout retry

---

### MCP Servers

| Server | Tools | Auth | Databases/Platforms |
|--------|-------|------|---------------------|
| **life-sciences-genomics** | 18 | NCBI_API_KEY (optional), COSMIC_API_KEY (required) | NCBI, Ensembl, ClinVar, GEO, SRA, COSMIC, gnomAD, dbSNP, ENCODE, 1000G, DDBJ |
| **life-sciences-proteomics** | 8 | None | UniProt, InterPro, Pfam, STRING, PRIDE, neXtProt |
| **life-sciences-structural** | 6 | None | PDB, AlphaFold DB, CATH, SCOP |
| **life-sciences-pathways** | 7 | None | KEGG, Reactome, BioCyc, WikiPathways, IntAct |
| **life-sciences-ontologies** | 6 | None | Gene Ontology, HPO, Disease Ontology |
| **life-sciences-clinical** | 10 | OMIM_API_KEY, DRUGBANK_API_KEY | OMIM, DrugBank, ChEMBL, PharmGKB, OpenTargets, FDA FAERS, ClinicalTrials.gov |
| **life-sciences-model-organisms** | 5 | None | FlyBase, WormBase, ZFIN, MGI, SGD |
| **life-sciences-molbio** | 9 | None | BLAST, Clustal Omega, MUSCLE, HMMER, Primer3, PrimerBLAST, REBASE |
| **life-sciences-cheminformatics** | 8 | CHEMSPIDER_API_KEY (for ChemSpider) | PubChem, ChemSpider, ZINC, RDKit, SwissDock, ADMET |
| **life-sciences-immunology** | 4 | IMMPORT_USERNAME + IMMPORT_PASSWORD | IEDB, ImmPort, IMGT, abYsis |
| **life-sciences-microbiology** | 8 | None | SILVA, Greengenes, QIIME 2, MG-RAST, BV-BRC, CARD |
| **life-sciences-metabolomics** | 4 | None | HMDB, MetaboLights, METLIN, MassBank |
| **life-sciences-epigenomics** | 3 | None | IHEC, Roadmap Epigenomics, MethBase |
| **life-sciences-imaging** | 7 | None (OMERO may need credentials) | OMERO, CellProfiler, ImageJ, DICOM, BioImage Archive, IDR, EMPIAR |
| **life-sciences-agriculture** | 4 | None | Phytozome, TAIR, Gramene, PlantGDB |
| **life-sciences-ecology** | 7 | IUCN_API_KEY (for IUCN Red List) | GBIF, BOLD, iNaturalist, IUCN Red List, GenBank Env, MGnify |
| **life-sciences-neuroscience** | 5 | None | Allen Brain Atlas, NeuroMorpho, OpenNeuro, BrainMap |
| **life-sciences-cellbiology** | 4 | None | Cell Atlas, CellxGene, Single Cell Expression Atlas |
| **life-sciences-healthcare** | 8 | REDCAP_API_TOKEN (for REDCap) | FHIR, HL7 v2, OMOP CDM, REDCap, DICOMweb |
| **life-sciences-biobanking** | 6 | None (LIMS may need credentials) | BBMRI, BioSample, LIMS, protocols.io |
| **life-sciences-pipelines** | 8 | None | nf-core, GATK/Broad (WDL), CWL Community, GitHub Community |
| **life-sciences-datastandards** | 7 | None | MAGE-TAB, ISA-Tab, SBML, BioPAX |
| **life-sciences-cloud** | 7 | TERRA_TOKEN (for Terra) | AWS Batch, Terra, Galaxy |
| **life-sciences-aiml** | 6 | None | ESM, AlphaFold, BioNLP (BioGPT/PubMedBERT) |


## PART 3: EXAMPLE TEST CASES

For each MCP server, here are example prompts to test in Kiro chat after
activating the Power and configuring the server in mcp.json.

### life-sciences-genomics

- "Search NCBI gene database for BRCA1" → Returns gene IDs and basic info
- "Fetch the nucleotide sequence for accession NM_007294.4 in FASTA format" → Returns FASTA sequence
- "Search PubMed for recent papers on CRISPR gene editing" → Returns article titles, authors, abstracts
- "Look up variants in the region 7:140424943-140624564 in Ensembl" → Returns variant IDs with consequences
- "Search ClinVar for the variant rs113488022" → Returns clinical significance and conditions

### life-sciences-proteomics

- "Search UniProt for the protein TP53" → Returns P04637 with protein name, organism, length
- "Get the full protein record for UniProt accession P04637" → Returns function, cross-refs, sequence
- "Find protein-protein interactions for TP53 in STRING" → Returns partners with confidence scores
- "Look up InterPro domain IPR011364" → Returns domain name, type, cross-references

### life-sciences-structural

- "Search PDB for hemoglobin structures" → Returns PDB IDs like 4HHB with resolution
- "Get the AlphaFold predicted structure for UniProt P04637" → Returns structure with pLDDT scores
- "Classify CATH domain 1cukA01" → Returns class, architecture, topology, superfamily
- "Download the PDB file for structure 4HHB" → Returns PDB-format coordinates

### life-sciences-pathways

- "Search KEGG for the apoptosis pathway" → Returns pathway ID (hsa04210) with genes
- "Get Reactome pathway R-HSA-1640170" → Returns pathway name, species, molecules
- "Find WikiPathways related to cell cycle in Homo sapiens" → Returns pathway IDs with names

### life-sciences-ontologies

- "Search Gene Ontology for 'kinase activity'" → Returns GO terms with IDs and namespaces
- "Get details for GO term GO:0008150" → Returns term name (biological_process), definition
- "Search HPO for 'seizure'" → Returns HPO terms with associated diseases

### life-sciences-clinical

- "Search OMIM for Marfan syndrome" (requires OMIM_API_KEY) → Returns MIM 154700
- "Search ChEMBL for aspirin" → Returns CHEMBL25 with formula and weight
- "Search ClinicalTrials.gov for breast cancer trials" → Returns NCT numbers, phases
- "Search FDA FAERS for adverse events related to aspirin" → Returns event reports

### life-sciences-model-organisms

- "Look up the gene dpp in FlyBase" → Returns FlyBase ID, location, phenotypes
- "Search for gene unc-86 in WormBase" → Returns WormBase ID, GO annotations
- "Look up Trp53 in MGI (mouse)" → Returns MGI ID, chromosomal location

### life-sciences-molbio

- "Submit a BLAST search for sequence ATGGATTTTATCTGCTCTTCG" → Returns RID
- "Design PCR primers for sequence with product size 150-250bp" → Returns primer pairs with Tm, GC%
- "Find restriction enzyme cut sites in GAATTCATGCGATCGAATTC" → Returns EcoRI sites
- "Look up restriction enzyme EcoRI in REBASE" → Returns recognition sequence, cut positions

### life-sciences-cheminformatics

- "Search PubChem for caffeine" → Returns CID, formula C8H10N4O2, MW
- "Compute molecular descriptors for SMILES CN1C=NC2=C1C(=O)N(C(=O)N2C)C" → Returns MW, LogP, HBD, HBA
- "Predict ADMET properties for aspirin" → Returns solubility, BBB, CYP450 predictions

### life-sciences-immunology

- "Search IEDB for epitopes from SARS-CoV-2 spike protein" → Returns epitopes with MHC alleles
- "Analyze this antibody sequence with abYsis" → Returns CDR annotations, framework regions

### life-sciences-microbiology

- "Search CARD for resistance genes related to tetracycline" → Returns ARO accessions, mechanisms
- "Search BV-BRC for Staphylococcus aureus genomes" → Returns genome IDs, contig counts
- "Search SILVA for Lactobacillus rRNA sequences" → Returns accessions with taxonomy

### life-sciences-metabolomics

- "Search HMDB for glucose" → Returns HMDB ID, formula, biological role, pathways
- "Search METLIN for metabolites with exact mass 180.063" → Returns matching metabolites
- "Search MassBank for caffeine spectra" → Returns spectral records with peaks

### life-sciences-epigenomics

- "Search IHEC for liver epigenome datasets" → Returns dataset IDs with tissue and marks
- "Search Roadmap Epigenomics for H3K4me3 in brain tissue" → Returns experiment IDs

### life-sciences-imaging

- "Search BioImage Archive for fluorescence microscopy datasets" → Returns accessions
- "Search EMPIAR for cryo-EM datasets" → Returns EMPIAR IDs with resolution
- "Query DICOM studies for modality CT" → Returns study metadata

### life-sciences-agriculture

- "Search TAIR for the gene FLC in Arabidopsis" → Returns locus ID, GO annotations
- "Search Gramene for rice genes related to drought tolerance" → Returns gene IDs

### life-sciences-ecology

- "Search GBIF for occurrences of Panthera tigris" → Returns records with coordinates
- "Get IUCN Red List status for Panthera tigris" (requires IUCN_API_KEY) → Returns Endangered status
- "Search iNaturalist for observations of monarch butterflies" → Returns observations

### life-sciences-neuroscience

- "Search Allen Brain Atlas for BDNF gene expression" → Returns expression with brain regions
- "Search NeuroMorpho for pyramidal neurons in hippocampus" → Returns morphologies
- "Search OpenNeuro for fMRI datasets" → Returns dataset accessions

### life-sciences-cellbiology

- "Search CellxGene for single-cell datasets from lung tissue" → Returns datasets with cell counts
- "Get gene expression for TP53 in CellxGene dataset" → Returns expression by cell type
- "Search Cell Atlas for TP53 subcellular localization" → Returns organelle assignments

### life-sciences-healthcare

- "Search FHIR for Patient resources with name Smith" → Returns FHIR Patient JSON
- "Parse this HL7 message: MSH|^~\\&|..." → Returns parsed segments and fields
- "Search OMOP for concept 'diabetes mellitus'" → Returns concept IDs with domain

### life-sciences-biobanking

- "Search BBMRI for biobanks with breast cancer samples in Germany" → Returns biobank names
- "Search protocols.io for CRISPR protocols" → Returns protocol DOIs, titles

### life-sciences-pipelines

- "List available nf-core pipelines" → Returns pipeline names with versions
- "Get details for the nf-core/sarek pipeline" → Returns description, inputs, parameters
- "Search GitHub for popular RNA-seq pipelines" → Returns repos with star counts
- "How do I import nf-core/rnaseq into AWS HealthOmics?" → Returns step-by-step instructions

### life-sciences-datastandards

- "Validate this SBML model" → Returns validation results with errors/warnings
- "Parse this ISA-Tab investigation file" → Returns structured metadata

### life-sciences-cloud

- "List my Terra workspaces" (requires TERRA_TOKEN) → Returns workspace names
- "Submit an AWS Batch job with definition 'my-job-def' to queue 'my-queue'" → Returns job ID
- "List available tools on Galaxy (usegalaxy.org)" → Returns tool IDs and versions

### life-sciences-aiml

- "Get ESM protein embeddings for sequence MEEPQSDPSVEPPLSQETFS" → Returns embeddings, secondary structure
- "Submit an AlphaFold structure prediction" → Returns job ID and ETA
- "Extract biomedical entities from: 'BRCA1 mutations increase breast cancer risk'" → Returns gene/disease entities


## PART 4: ADVANCED TEST CASES (Multi-Step Workflows)

These test cases go beyond simple database queries. They test pipeline
execution, molecular design, compute job submission, data validation,
cross-database workflows, and AI/ML inference.

### Pipeline Execution (life-sciences-pipelines + aws-healthomics)

**Test 1:** "List nf-core pipelines, then show me how to import nf-core/sarek into AWS HealthOmics for somatic variant calling"
→ Lists pipelines → provides step-by-step import instructions including packaging, CreateWorkflow API call, and parameter config

**Test 2:** "Find a WDL pipeline for germline short variant discovery from the Broad Institute, and create an AWS HealthOmics workflow from it"
→ Finds GATK best practices pipeline → provides WDL packaging instructions → shows CreateAHOWorkflow parameters

**Test 3:** "Search GitHub for RNA-seq pipelines with 500+ stars, then help me run the top result on AWS HealthOmics"
→ Returns popular repos → provides import workflow for the selected pipeline

### Molecular Biology Design (life-sciences-molbio)

**Test 4:** "Design PCR primers for amplifying the BRCA1 exon 11 region with a product size of 200-400bp, then check their specificity against the human genome"
→ Primer3 returns primer pairs → PrimerBLAST checks specificity → reports off-target sites

**Test 5:** "Clone my insert into pUC19 using EcoRI and BamHI. Analyze the restriction sites and design the cloning strategy"
→ Restriction analysis → identifies compatible sites → designs construct with junction sequences

**Test 6:** "Submit a BLAST search for this protein sequence, then show me the top 5 hits with their domain architecture from InterPro"
→ BLAST submit → poll for results → InterPro lookup for each hit

### Computational Chemistry (life-sciences-cheminformatics)

**Test 7:** "Search PubChem for ibuprofen, compute its molecular descriptors, check Lipinski compliance, and predict ADMET properties"
→ PubChem CID → RDKit descriptors → Lipinski check → ADMET predictions

**Test 8:** "I have a receptor (PDB: 1HWI) and a ligand (SMILES: CC(=O)Oc1ccccc1C(=O)O). Submit a molecular docking job"
→ Docking submit → returns binding affinity scores and interacting residues

**Test 9:** "Search ZINC for drug-like compounds similar to aspirin (LogP < 2, MW < 300), then compute RDKit descriptors for the top 5"
→ ZINC filtered search → RDKit descriptors for each compound

### Cross-Database Workflows

**Test 10:** "Cross-database search for gene BRCA1 — results from NCBI, UniProt, Ensembl, ClinVar, OMIM, and Gene Ontology"
→ Parallel queries to 6 databases → consolidated results grouped by database

**Test 11:** "Search for metformin across DrugBank, ChEMBL, PharmGKB, and OpenTargets"
→ DrugBank targets → ChEMBL bioactivity → PharmGKB annotations → OpenTargets associations

**Test 12:** "Study protein TP53: UniProt sequence, PDB structures, AlphaFold prediction, STRING interactions, InterPro domains"
→ Comprehensive TP53 profile from 5 databases

### Cloud Compute (life-sciences-cloud)

**Test 13:** "Submit an AWS Batch job using job definition 'variant-calling-job' on queue 'genomics-queue', then check its status"
→ Batch submit returns job ID → status query returns RUNNING/SUCCEEDED

**Test 14:** "List my Terra workspaces, then submit a workflow to 'my-genomics-workspace'"
→ Lists workspaces → submits workflow → returns submission ID

**Test 15:** "Find the BWA-MEM tool on Galaxy, then submit a job with my FASTQ files"
→ Galaxy tool search → submits job → returns job ID

### Data Validation (life-sciences-datastandards)

**Test 16:** "Validate this SBML model against Level 3 Version 2, then parse it and show compartments, species, and reactions"
→ SBML validation → parse returns structured model components

**Test 17:** "Validate my ISA-Tab investigation file and check MINSEQE compliance"
→ ISA-Tab validation → compliance checklist assessment

**Test 18:** "Parse this BioPAX pathway file and show pathways, interactions, and physical entities"
→ BioPAX parse returns structured pathway components

### Clinical Data Integration (life-sciences-healthcare)

**Test 19:** "Search FHIR for patients with condition 'diabetes', then create a new Observation for patient P001 with HbA1c 7.2%"
→ FHIR search → FHIR create → returns resource ID

**Test 20:** "Parse this HL7 v2 ADT^A01 message, extract demographics, then generate a new message with updated address"
→ HL7 parse → structured segments → HL7 generate with modifications

**Test 21:** "Export all records from REDCap project 12345 in JSON, then map fields to OMOP CDM concepts"
→ REDCap export → OMOP concept mapping suggestions

### AI/ML Inference (life-sciences-aiml)

**Test 22:** "Get ESM embeddings for sequence MEEPQSDPSVEPPLSQETFS, predict secondary structure, and generate a contact map"
→ Per-residue embeddings, secondary structure predictions, contact map

**Test 23:** "Submit this protein sequence for AlphaFold prediction, then check job status"
→ AlphaFold submit → status check with progress and ETA

**Test 24:** "Extract biomedical entities from this abstract about BRCA1/BRCA2 and Olaparib, then answer: What drugs target BRCA-mutated cancers?"
→ Entity extraction (genes, diseases, drugs) → QA returns "Olaparib" with confidence

### Microbiome Analysis (life-sciences-microbiology)

**Test 25:** "Run QIIME 2 diversity analysis on 16S data, search SILVA for top OTU taxonomy, check CARD for resistance genes"
→ QIIME 2 diversity → SILVA taxonomy → CARD resistance search

**Test 26:** "Search BV-BRC for M. tuberculosis genomes, get features, then check CARD for resistance determinants"
→ BV-BRC search → features → CARD analysis

### Ecology Workflows (life-sciences-ecology)

**Test 27:** "Search GBIF for Panthera tigris in India, get IUCN status, find recent iNaturalist observations"
→ GBIF occurrences → IUCN Endangered → iNaturalist observations

**Test 28:** "Search MGnify for soil metagenome studies, get taxonomic summary for top result"
→ MGnify search → taxonomic composition data

### Immunology & Vaccine Design (life-sciences-immunology)

**Test 29:** "Search IEDB for T-cell epitopes from SARS-CoV-2 spike restricted to HLA-A*02:01, then analyze with abYsis"
→ IEDB epitope search → abYsis sequence analysis with CDR annotations

### Single-Cell Analysis (life-sciences-cellbiology)

**Test 30:** "Search CellxGene for human lung datasets, then get ACE2 expression across cell types"
→ CellxGene search → ACE2 expression grouped by cell type
