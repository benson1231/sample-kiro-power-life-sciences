# Common Queries & Test Cases

Example prompts to test in Kiro chat after activating the Power and configuring MCP servers in `mcp.json`.

---

## Basic Queries (Per MCP Server)

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

---

## Advanced Test Cases (Multi-Step Workflows)

These test cases go beyond simple database queries. They test pipeline execution, molecular design, compute job submission, data validation, cross-database workflows, and AI/ML inference.

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
