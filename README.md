================================================================================
KIRO FOR LIFE SCIENCES — TESTER DEPLOYMENT GUIDE
================================================================================

================================================================================
WHAT IS THIS?
================================================================================

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

Disciplines covered:
  Genomics & Sequencing | Proteomics | Structural Biology | Pathways |
  Ontologies | Clinical & Pharma | Model Organisms | Molecular Biology |
  Computational Chemistry | Immunology | Microbiology & Metagenomics |
  Metabolomics | Epigenomics | Imaging & Microscopy | Agriculture & Plants |
  Ecology & Environment | Neuroscience | Cell Biology | Healthcare Standards |
  Biobanking | Pipelines | Data Standards | Cloud & HPC | AI/ML

What you can do with it:
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


================================================================================
PART 1: DEPLOYMENT INSTRUCTIONS
================================================================================

Prerequisites:
- Kiro IDE installed
- Python 3.10 or higher
- uv package manager (install: curl -LsSf https://astral.sh/uv/install.sh | sh)

Step 1: Unzip the package
-------------------------
Unzip kiro-life-sciences.zip to a location of your choice:

    unzip kiro-life-sciences.zip -d ~/kiro-life-sciences-project
    cd ~/kiro-life-sciences-project/KiroLS

Step 2: Create a virtual environment and install packages
---------------------------------------------------------
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

Step 3: Copy the Power into Kiro
---------------------------------
    cp -r kiro-life-sciences/ ~/.kiro/powers/kiro-life-sciences/

    This makes the Power available in Kiro's Powers panel with its skills,
    steering files, and onboarding dashboard.

Step 4: Configure MCP servers in your workspace
------------------------------------------------
Create or edit .kiro/settings/mcp.json in your Kiro workspace:

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

Replace /path/to/KiroLS/ with the actual path where you unzipped.
Add only the servers you installed in Step 2.

Step 5: Configure credentials (optional)
-----------------------------------------
For databases that require API keys, add env vars:

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

Step 6: Verify installation
----------------------------
Run the test suite to confirm everything works:

    cd ~/kiro-life-sciences-project/KiroLS
    source .venv/bin/activate
    pytest kiro-life-sciences/tests/ -q
    pytest life-sciences-common/tests/ -q

Expected: 338+ tests passing for kiro-life-sciences, 32 for life-sciences-common.

Step 7: Test in Kiro
---------------------
1. Open Kiro
2. Activate the "kiro-life-sciences" Power from the Powers panel
3. Try asking: "Search NCBI for BRCA1" or "Look up TP53 in UniProt"
4. The Power's tools should be available in chat


================================================================================
PART 2: PACKAGE CONTENTS BY SUBDIRECTORY
================================================================================

kiro-life-sciences/                    [CENTRAL POWER - Hub]
├── POWER.md                           Documentation and getting-started guide
├── pyproject.toml                     Package config (pydantic, httpx, pytest, hypothesis)
├── bundle-manifest.json               Declares all 24 MCP servers, 10 skills, 16 steering files
├── skills/                            10 domain-specific skill files
│   ├── bioinformatics-file-formats.md    FASTA, FASTQ, BAM, VCF, GFF, BED, DICOM, SBML formats
│   ├── genomics-pipeline-best-practices.md  WDL/Nextflow/CWL design patterns
│   ├── data-compliance.md                HIPAA, GDPR, GxP, MIAME, MINSEQE
│   ├── clinical-interoperability.md      FHIR, HL7, OMOP CDM
│   ├── ecological-data-analysis.md       Species distribution, biodiversity, eDNA
│   ├── cheminformatics-best-practices.md SMILES, InChI, Lipinski, SAR
│   ├── biomedical-imaging.md             Segmentation, feature extraction, DICOM
│   ├── immunology-vaccine-design.md      Epitope prediction, MHC binding, antibodies
│   ├── metabolomics-analysis.md          Metabolite ID, spectral matching
│   └── single-cell-analysis.md           QC, clustering, trajectory inference
├── steering/                          16 step-by-step workflow guides
│   ├── variant-calling-pipeline.md       HealthOmics variant calling setup
│   ├── gene-disease-associations.md      ClinVar → OMIM → HPO cross-referencing
│   ├── protein-structure-analysis.md     PDB → AlphaFold → CATH workflows
│   ├── pipeline-import-healthomics.md    Import nf-core/WDL into HealthOmics
│   ├── resource-catalog-browsing.md      How to search/browse the catalog
│   ├── fhir-clinical-integration.md      FHIR + OMOP CDM workflows
│   ├── species-distribution-analysis.md  GBIF → IUCN → iNaturalist
│   ├── metabolite-identification.md      HMDB → MetaboLights → MassBank
│   ├── microbiome-analysis.md            SILVA → QIIME 2 → MG-RAST
│   ├── compound-screening.md             PubChem → RDKit → ZINC → docking
│   ├── biomedical-image-analysis.md      OMERO → CellProfiler → ImageJ
│   ├── molecular-docking.md              PDB → ligand prep → SwissDock
│   ├── primer-design-cloning.md          Primer3 → PrimerBLAST → REBASE
│   ├── single-cell-rnaseq.md             CellxGene → expression analysis
│   ├── epigenomics-analysis.md           IHEC → Roadmap → ENCODE
│   └── amr-analysis.md                   CARD → BV-BRC resistance profiling
└── src/kiro_life_sciences/            Core Python modules
    ├── models/                        Pydantic data models (manifest, catalog)
    ├── catalog/                       Resource catalog engine (search, browse, filter)
    ├── dashboard/                     Onboarding dashboard renderer
    ├── credentials/                   Credential manager (${secret:key} in mcp.json)
    ├── installer/                     Bundle installer, dependency resolver, updater
    └── skills/                        Cross-database search skill

life-sciences-common/                  [SHARED BASE PACKAGE]
├── BaseLifeSciencesServer             Async HTTP client with retry logic
├── Error classes                      RateLimitError, AuthenticationError, NotFoundError, etc.
└── Exponential backoff                429 retry, 5xx retry, timeout retry

life-sciences-genomics/                [MCP SERVER - Genomics & Sequencing]
├── 18 tools                           NCBI search/fetch, Ensembl gene/variants/sequence,
│                                      ClinVar search, GEO/SRA search, COSMIC mutations,
│                                      gnomAD frequencies, dbSNP lookup, ENCODE experiments,
│                                      1000 Genomes frequencies, DDBJ search/fetch
├── Auth: NCBI_API_KEY (optional), COSMIC_API_KEY (required)
└── Databases: NCBI, Ensembl, ClinVar, GEO, SRA, COSMIC, gnomAD, dbSNP, ENCODE, 1000G, DDBJ

life-sciences-proteomics/              [MCP SERVER - Proteomics]
├── 8 tools                            UniProt search/fetch/sequence, InterPro lookup,
│                                      Pfam family, STRING interactions, PRIDE search,
│                                      neXtProt entry
├── Auth: None required
└── Databases: UniProt, InterPro, Pfam, STRING, PRIDE, neXtProt

life-sciences-structural/              [MCP SERVER - Structural Biology]
├── 6 tools                            PDB search/fetch/download, AlphaFold lookup,
│                                      CATH classify, SCOP classify
├── Auth: None required
└── Databases: PDB, AlphaFold DB, CATH, SCOP

life-sciences-pathways/                [MCP SERVER - Pathways & Interactions]
├── 7 tools                            KEGG pathway/search, Reactome search/pathway,
│                                      BioCyc pathway, WikiPathways search, IntAct interactions
├── Auth: None required
└── Databases: KEGG, Reactome, BioCyc, WikiPathways, IntAct

life-sciences-ontologies/              [MCP SERVER - Ontologies]
├── 6 tools                            GO search/term/annotations, HPO search/term,
│                                      Disease Ontology search
├── Auth: None required
└── Databases: Gene Ontology, HPO, Disease Ontology

life-sciences-clinical/                [MCP SERVER - Clinical & Pharma]
├── 10 tools                           OMIM search/entry, DrugBank search/drug,
│                                      ChEMBL search/bioactivity, PharmGKB search,
│                                      OpenTargets search, FDA FAERS search,
│                                      ClinicalTrials.gov search
├── Auth: OMIM_API_KEY (required), DRUGBANK_API_KEY (required)
└── Databases: OMIM, DrugBank, ChEMBL, PharmGKB, OpenTargets, FDA FAERS, ClinicalTrials.gov

life-sciences-model-organisms/         [MCP SERVER - Model Organisms]
├── 5 tools                            FlyBase gene, WormBase gene, ZFIN gene,
│                                      MGI gene, SGD gene
├── Auth: None required
└── Databases: FlyBase, WormBase, ZFIN, MGI, SGD

life-sciences-molbio/                  [MCP SERVER - Molecular Biology]
├── 9 tools                            BLAST search/results, MSA align, HMMER search,
│                                      Primer3 design, PrimerBLAST, restriction analysis,
│                                      REBASE enzyme, cloning design
├── Auth: None required
└── Tools: BLAST, Clustal Omega, MUSCLE, HMMER, Primer3, PrimerBLAST, REBASE

life-sciences-cheminformatics/         [MCP SERVER - Computational Chemistry]
├── 8 tools                            PubChem search/properties, ChemSpider search,
│                                      ZINC search, RDKit descriptors/substructure,
│                                      docking submit, ADMET predict
├── Auth: CHEMSPIDER_API_KEY (required for ChemSpider)
└── Databases: PubChem, ChemSpider, ZINC, RDKit, SwissDock, ADMET

life-sciences-immunology/              [MCP SERVER - Immunology]
├── 4 tools                            IEDB search, ImmPort search, IMGT search,
│                                      abYsis analyze
├── Auth: IMMPORT_USERNAME + IMMPORT_PASSWORD (required for ImmPort)
└── Databases: IEDB, ImmPort, IMGT, abYsis

life-sciences-microbiology/            [MCP SERVER - Microbiology & Metagenomics]
├── 8 tools                            SILVA search, Greengenes search, QIIME 2 action,
│                                      MG-RAST search, BV-BRC search/features,
│                                      CARD search/analyze
├── Auth: None required
└── Databases: SILVA, Greengenes, QIIME 2, MG-RAST, BV-BRC, CARD

life-sciences-metabolomics/            [MCP SERVER - Metabolomics]
├── 4 tools                            HMDB search, MetaboLights search,
│                                      METLIN search, MassBank search
├── Auth: None required
└── Databases: HMDB, MetaboLights, METLIN, MassBank

life-sciences-epigenomics/             [MCP SERVER - Epigenomics]
├── 3 tools                            IHEC search, Roadmap search, MethBase search
├── Auth: None required
└── Databases: IHEC, Roadmap Epigenomics, MethBase

life-sciences-imaging/                 [MCP SERVER - Imaging & Microscopy]
├── 7 tools                            OMERO search, CellProfiler run, ImageJ macro,
│                                      DICOM query, BioImage search, IDR search, EMPIAR search
├── Auth: None required (OMERO may need server credentials)
└── Tools: OMERO, CellProfiler, ImageJ, DICOM, BioImage Archive, IDR, EMPIAR

life-sciences-agriculture/             [MCP SERVER - Plant Biology]
├── 4 tools                            Phytozome search, TAIR search,
│                                      Gramene search, PlantGDB search
├── Auth: None required
└── Databases: Phytozome, TAIR, Gramene, PlantGDB

life-sciences-ecology/                 [MCP SERVER - Ecology & Environment]
├── 7 tools                            GBIF occurrences/taxonomy, BOLD search,
│                                      iNaturalist search, IUCN species,
│                                      GenBank env search, MGnify search
├── Auth: IUCN_API_KEY (required for IUCN Red List)
└── Databases: GBIF, BOLD, iNaturalist, IUCN Red List, GenBank Env, MGnify

life-sciences-neuroscience/            [MCP SERVER - Neuroscience]
├── 5 tools                            Allen Brain search/structure, NeuroMorpho search,
│                                      OpenNeuro search, BrainMap search
├── Auth: None required
└── Databases: Allen Brain Atlas, NeuroMorpho, OpenNeuro, BrainMap

life-sciences-cellbiology/             [MCP SERVER - Cell Biology]
├── 4 tools                            Cell Atlas search, CellxGene datasets/expression,
│                                      Single Cell Expression Atlas search
├── Auth: None required
└── Databases: Cell Atlas, CellxGene, Single Cell Expression Atlas

life-sciences-healthcare/              [MCP SERVER - Healthcare Standards]
├── 8 tools                            FHIR search/create, HL7 parse/generate,
│                                      OMOP search, REDCap records/export, DICOMweb query
├── Auth: REDCAP_API_TOKEN (required for REDCap)
└── Standards: FHIR, HL7 v2, OMOP CDM, REDCap, DICOMweb

life-sciences-biobanking/              [MCP SERVER - Biobanking & Samples]
├── 6 tools                            BBMRI search, BioSample search, LIMS sample/create,
│                                      inventory search, protocols.io search
├── Auth: None required (LIMS may need credentials)
└── Databases: BBMRI, BioSample, LIMS, protocols.io

life-sciences-pipelines/               [MCP SERVER - Pipeline Registry]
├── 8 tools                            nf-core list/pipeline, WDL list/pipeline,
│                                      CWL list/pipeline, GitHub pipelines,
│                                      HealthOmics import instructions
├── Auth: None required
└── Registries: nf-core, GATK/Broad (WDL), CWL Community, GitHub Community

life-sciences-datastandards/           [MCP SERVER - Data Standards]
├── 7 tools                            MAGE-TAB validate/parse, ISA-Tab validate/parse,
│                                      SBML validate/parse, BioPAX parse
├── Auth: None required
└── Standards: MAGE-TAB, ISA-Tab, SBML, BioPAX

life-sciences-cloud/                   [MCP SERVER - Cloud & HPC]
├── 7 tools                            AWS Batch submit/status, Terra workspaces/submit,
│                                      Galaxy tools/submit/status
├── Auth: TERRA_TOKEN (required for Terra)
└── Platforms: AWS Batch, Terra, Galaxy

life-sciences-aiml/                    [MCP SERVER - AI/ML]
├── 6 tools                            ESM embeddings/structure, AlphaFold predict/status,
│                                      BioNLP entities/QA
├── Auth: None required
└── Models: ESM, AlphaFold, BioNLP (BioGPT/PubMedBERT)


================================================================================
PART 3: EXAMPLE TEST CASES BY SUBDIRECTORY
================================================================================

For each MCP server, here are example prompts to test in Kiro chat after
activating the Power and configuring the server in mcp.json.

--------------------------------------------------------------------------------
life-sciences-genomics
--------------------------------------------------------------------------------
Test 1: "Search NCBI gene database for BRCA1"
Expected: Returns gene IDs and basic info for BRCA1

Test 2: "Fetch the nucleotide sequence for accession NM_007294.4 in FASTA format"
Expected: Returns FASTA-formatted sequence data

Test 3: "Search PubMed for recent papers on CRISPR gene editing"
Expected: Returns article titles, authors, and abstracts

Test 4: "Look up variants in the region 7:140424943-140624564 in Ensembl"
Expected: Returns variant IDs with consequence types

Test 5: "Search ClinVar for the variant rs113488022"
Expected: Returns clinical significance and associated conditions

--------------------------------------------------------------------------------
life-sciences-proteomics
--------------------------------------------------------------------------------
Test 1: "Search UniProt for the protein TP53"
Expected: Returns P04637 with protein name, organism, sequence length

Test 2: "Get the full protein record for UniProt accession P04637"
Expected: Returns function annotation, cross-references, sequence

Test 3: "Find protein-protein interactions for TP53 in STRING"
Expected: Returns interaction partners with confidence scores

Test 4: "Look up InterPro domain IPR011364"
Expected: Returns domain name, type, and member database cross-references

--------------------------------------------------------------------------------
life-sciences-structural
--------------------------------------------------------------------------------
Test 1: "Search PDB for hemoglobin structures"
Expected: Returns PDB IDs like 4HHB with resolution and method

Test 2: "Get the AlphaFold predicted structure for UniProt P04637"
Expected: Returns structure with pLDDT confidence scores

Test 3: "Classify CATH domain 1cukA01"
Expected: Returns class, architecture, topology, homologous superfamily

Test 4: "Download the PDB file for structure 4HHB"
Expected: Returns PDB-format coordinate data

--------------------------------------------------------------------------------
life-sciences-pathways
--------------------------------------------------------------------------------
Test 1: "Search KEGG for the apoptosis pathway"
Expected: Returns pathway ID (hsa04210) with associated genes

Test 2: "Get Reactome pathway R-HSA-1640170"
Expected: Returns pathway name, species, participating molecules

Test 3: "Find WikiPathways related to cell cycle in Homo sapiens"
Expected: Returns pathway IDs with names and revision dates

--------------------------------------------------------------------------------
life-sciences-ontologies
--------------------------------------------------------------------------------
Test 1: "Search Gene Ontology for 'kinase activity'"
Expected: Returns GO terms with IDs, names, and namespaces

Test 2: "Get details for GO term GO:0008150"
Expected: Returns term name (biological_process), definition

Test 3: "Search HPO for 'seizure'"
Expected: Returns HPO terms with IDs and associated diseases

--------------------------------------------------------------------------------
life-sciences-clinical
--------------------------------------------------------------------------------
Test 1: "Search OMIM for Marfan syndrome" (requires OMIM_API_KEY)
Expected: Returns MIM number 154700 with title

Test 2: "Search ChEMBL for aspirin"
Expected: Returns CHEMBL25 with molecular formula and weight

Test 3: "Search ClinicalTrials.gov for breast cancer trials"
Expected: Returns NCT numbers, titles, phases, and enrollment

Test 4: "Search FDA FAERS for adverse events related to aspirin"
Expected: Returns adverse event reports with reactions and outcomes

--------------------------------------------------------------------------------
life-sciences-model-organisms
--------------------------------------------------------------------------------
Test 1: "Look up the gene dpp in FlyBase"
Expected: Returns FlyBase ID, cytological location, phenotypes

Test 2: "Search for gene unc-86 in WormBase"
Expected: Returns WormBase ID, genomic location, GO annotations

Test 3: "Look up Trp53 in MGI (mouse)"
Expected: Returns MGI ID, chromosomal location, phenotype annotations

--------------------------------------------------------------------------------
life-sciences-molbio
--------------------------------------------------------------------------------
Test 1: "Submit a BLAST search for sequence ATGGATTTTATCTGCTCTTCG"
Expected: Returns a request ID (RID) for the BLAST job

Test 2: "Design PCR primers for the sequence ATGCGATCGATCGATCG... with product size 150-250bp"
Expected: Returns primer pairs with Tm, GC%, and product size

Test 3: "Find restriction enzyme cut sites in GAATTCATGCGATCGAATTC"
Expected: Returns EcoRI sites at positions with fragment sizes

Test 4: "Look up restriction enzyme EcoRI in REBASE"
Expected: Returns recognition sequence GAATTC, cut positions, source organism

--------------------------------------------------------------------------------
life-sciences-cheminformatics
--------------------------------------------------------------------------------
Test 1: "Search PubChem for caffeine"
Expected: Returns CID, molecular formula C8H10N4O2, molecular weight

Test 2: "Compute molecular descriptors for SMILES string CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
Expected: Returns MW, LogP, H-bond donors/acceptors, Lipinski compliance

Test 3: "Predict ADMET properties for aspirin (SMILES: CC(=O)OC1=CC=CC=C1C(=O)O)"
Expected: Returns solubility, BBB permeability, CYP450 inhibition predictions

--------------------------------------------------------------------------------
life-sciences-immunology
--------------------------------------------------------------------------------
Test 1: "Search IEDB for epitopes from SARS-CoV-2 spike protein"
Expected: Returns epitope sequences with MHC alleles and assay types

Test 2: "Analyze this antibody sequence with abYsis: EVQLVESGGGLVQPGG..."
Expected: Returns CDR annotations, framework regions, numbering

--------------------------------------------------------------------------------
life-sciences-microbiology
--------------------------------------------------------------------------------
Test 1: "Search CARD for resistance genes related to tetracycline"
Expected: Returns ARO accessions, gene names, resistance mechanisms

Test 2: "Search BV-BRC for Staphylococcus aureus genomes"
Expected: Returns genome IDs, status, contig counts

Test 3: "Search SILVA for Lactobacillus rRNA sequences"
Expected: Returns accessions with taxonomic classification

--------------------------------------------------------------------------------
life-sciences-metabolomics
--------------------------------------------------------------------------------
Test 1: "Search HMDB for glucose"
Expected: Returns HMDB ID, chemical formula, biological role, pathways

Test 2: "Search METLIN for metabolites with exact mass 180.063"
Expected: Returns matching metabolites within tolerance

Test 3: "Search MassBank for caffeine spectra"
Expected: Returns spectral records with instrument type and peaks

--------------------------------------------------------------------------------
life-sciences-epigenomics
--------------------------------------------------------------------------------
Test 1: "Search IHEC for liver epigenome datasets"
Expected: Returns dataset IDs with tissue, assay, and epigenomic marks

Test 2: "Search Roadmap Epigenomics for H3K4me3 in brain tissue"
Expected: Returns experiment IDs with chromatin state annotations

--------------------------------------------------------------------------------
life-sciences-imaging
--------------------------------------------------------------------------------
Test 1: "Search BioImage Archive for fluorescence microscopy datasets"
Expected: Returns accessions with imaging modality and organism

Test 2: "Search EMPIAR for cryo-EM datasets"
Expected: Returns EMPIAR IDs with resolution and data size

Test 3: "Query DICOM studies for modality CT"
Expected: Returns study metadata with body part and image count

--------------------------------------------------------------------------------
life-sciences-agriculture
--------------------------------------------------------------------------------
Test 1: "Search TAIR for the gene FLC in Arabidopsis"
Expected: Returns locus ID, chromosomal location, GO annotations

Test 2: "Search Gramene for rice genes related to drought tolerance"
Expected: Returns gene IDs with species and pathway associations

--------------------------------------------------------------------------------
life-sciences-ecology
--------------------------------------------------------------------------------
Test 1: "Search GBIF for occurrences of Panthera tigris"
Expected: Returns occurrence records with coordinates and dates

Test 2: "Get IUCN Red List status for Panthera tigris" (requires IUCN_API_KEY)
Expected: Returns Endangered status, population trend, threats

Test 3: "Search iNaturalist for observations of monarch butterflies"
Expected: Returns observation records with locations and quality grades

--------------------------------------------------------------------------------
life-sciences-neuroscience
--------------------------------------------------------------------------------
Test 1: "Search Allen Brain Atlas for BDNF gene expression"
Expected: Returns expression data with brain regions and energy values

Test 2: "Search NeuroMorpho for pyramidal neurons in hippocampus"
Expected: Returns neuron morphologies with cell type and species

Test 3: "Search OpenNeuro for fMRI datasets"
Expected: Returns dataset accessions with participant counts

--------------------------------------------------------------------------------
life-sciences-cellbiology
--------------------------------------------------------------------------------
Test 1: "Search CellxGene for single-cell datasets from lung tissue"
Expected: Returns dataset IDs with cell counts and assay types

Test 2: "Get gene expression for TP53 in CellxGene dataset X"
Expected: Returns expression values grouped by cell type

Test 3: "Search Cell Atlas for TP53 subcellular localization"
Expected: Returns organelle assignments with reliability scores

--------------------------------------------------------------------------------
life-sciences-healthcare
--------------------------------------------------------------------------------
Test 1: "Search FHIR for Patient resources with name Smith"
Expected: Returns FHIR Patient resources in JSON format

Test 2: "Parse this HL7 message: MSH|^~\&|SendApp|SendFac|..."
Expected: Returns parsed segments and fields in structured format

Test 3: "Search OMOP for concept 'diabetes mellitus'"
Expected: Returns concept IDs with domain and vocabulary

--------------------------------------------------------------------------------
life-sciences-biobanking
--------------------------------------------------------------------------------
Test 1: "Search BBMRI for biobanks with breast cancer samples in Germany"
Expected: Returns biobank names, collection names, sample counts

Test 2: "Search protocols.io for CRISPR protocols"
Expected: Returns protocol DOIs, titles, authors, step counts

--------------------------------------------------------------------------------
life-sciences-pipelines
--------------------------------------------------------------------------------
Test 1: "List available nf-core pipelines"
Expected: Returns pipeline names (rnaseq, sarek, viralrecon, etc.) with versions

Test 2: "Get details for the nf-core/sarek pipeline"
Expected: Returns description, required inputs, parameters, repository URL

Test 3: "Search GitHub for popular RNA-seq pipelines"
Expected: Returns repositories with star counts and descriptions

Test 4: "How do I import nf-core/rnaseq into AWS HealthOmics?"
Expected: Returns step-by-step import instructions

--------------------------------------------------------------------------------
life-sciences-datastandards
--------------------------------------------------------------------------------
Test 1: "Validate this SBML model: <sbml>...</sbml>"
Expected: Returns validation results with any errors/warnings

Test 2: "Parse this ISA-Tab investigation file"
Expected: Returns structured investigation/study/assay metadata

--------------------------------------------------------------------------------
life-sciences-cloud
--------------------------------------------------------------------------------
Test 1: "List my Terra workspaces" (requires TERRA_TOKEN)
Expected: Returns workspace names, namespaces, creation dates

Test 2: "Submit an AWS Batch job with definition 'my-job-def' to queue 'my-queue'"
Expected: Returns job ID and submission status

Test 3: "List available tools on Galaxy (usegalaxy.org)"
Expected: Returns tool IDs, names, versions, descriptions

--------------------------------------------------------------------------------
life-sciences-aiml
--------------------------------------------------------------------------------
Test 1: "Get ESM protein embeddings for sequence MEEPQSDPSVEPPLSQETFS"
Expected: Returns per-residue embeddings and secondary structure predictions

Test 2: "Submit an AlphaFold structure prediction for sequence MEEPQSDP..."
Expected: Returns job ID and estimated completion time

Test 3: "Extract biomedical entities from: 'BRCA1 mutations increase breast cancer risk'"
Expected: Returns entities: BRCA1 (gene), breast cancer (disease)


================================================================================
END OF GUIDE
================================================================================


================================================================================
PART 4: ADVANCED TEST CASES (Multi-Step Workflows)
================================================================================

These test cases go beyond simple database queries. They test pipeline
execution, molecular design, compute job submission, data validation,
cross-database workflows, and AI/ML inference.

--------------------------------------------------------------------------------
PIPELINE EXECUTION (life-sciences-pipelines + aws-healthomics)
--------------------------------------------------------------------------------

Test 1: "List nf-core pipelines, then show me how to import nf-core/sarek
         into AWS HealthOmics for somatic variant calling"
Expected: Lists pipelines → provides step-by-step import instructions
          including packaging, CreateWorkflow API call, and parameter config

Test 2: "Find a WDL pipeline for germline short variant discovery from the
         Broad Institute, and create an AWS HealthOmics workflow from it"
Expected: Finds GATK best practices pipeline → provides WDL packaging
          instructions → shows CreateAHOWorkflow parameters

Test 3: "Search GitHub for RNA-seq pipelines with 500+ stars, then help me
         run the top result on AWS HealthOmics"
Expected: Returns popular repos → provides import workflow for the selected
          pipeline including input parameter mapping

--------------------------------------------------------------------------------
MOLECULAR BIOLOGY DESIGN (life-sciences-molbio)
--------------------------------------------------------------------------------

Test 4: "Design PCR primers for amplifying the BRCA1 exon 11 region with a
         product size of 200-400bp, then check their specificity against the
         human genome"
Expected: Primer3 returns primer pairs → PrimerBLAST checks specificity →
          reports off-target sites and mismatch counts

Test 5: "I want to clone my insert (ATGCGATCG...) into pUC19 using EcoRI and
         BamHI. Analyze the restriction sites in both sequences and design
         the cloning strategy"
Expected: Restriction analysis of both sequences → identifies compatible
          sites → designs the construct with junction sequences and total size

Test 6: "Submit a BLAST search for this protein sequence against the nr
         database, then when results are ready, show me the top 5 hits with
         their domain architecture from InterPro"
Expected: BLAST submit → poll for results → fetch top hits → InterPro
          lookup for each hit showing domain annotations

--------------------------------------------------------------------------------
COMPUTATIONAL CHEMISTRY (life-sciences-cheminformatics)
--------------------------------------------------------------------------------

Test 7: "Search PubChem for ibuprofen, compute its molecular descriptors,
         check Lipinski rule-of-five compliance, and predict its ADMET
         properties"
Expected: PubChem returns CID → RDKit computes MW, LogP, HBD, HBA →
          reports Lipinski compliance → ADMET predicts solubility, BBB, CYP450

Test 8: "I have a receptor (PDB: 1HWI) and a ligand (SMILES: CC(=O)Oc1ccccc1C(=O)O).
         Submit a molecular docking job and analyze the binding poses"
Expected: Docking submit with receptor PDB ID and ligand SMILES →
          returns binding affinity scores and interacting residues

Test 9: "Search ZINC for drug-like compounds similar to aspirin (LogP < 2,
         MW < 300), then compute RDKit descriptors for the top 5"
Expected: ZINC filtered search → returns compounds → RDKit descriptors
          for each with Lipinski assessment

--------------------------------------------------------------------------------
CROSS-DATABASE WORKFLOWS (cross-database search + multiple servers)
--------------------------------------------------------------------------------

Test 10: "Do a cross-database search for gene BRCA1 — I want results from
          NCBI, UniProt, Ensembl, ClinVar, OMIM, and Gene Ontology"
Expected: Parallel queries to all 6 databases → consolidated results
          grouped by database → reports any unavailable databases

Test 11: "Search for the drug metformin across DrugBank, ChEMBL, PharmGKB,
          and OpenTargets. Show me targets, bioactivity, and clinical
          annotations"
Expected: Cross-database drug search → DrugBank targets → ChEMBL
          bioactivity data → PharmGKB clinical annotations → OpenTargets
          disease associations

Test 12: "I'm studying the protein TP53. Search UniProt for its sequence,
          PDB for experimental structures, AlphaFold for predicted structure,
          STRING for interaction partners, and InterPro for domain architecture"
Expected: Cross-database protein search → comprehensive TP53 profile
          from 5 databases

--------------------------------------------------------------------------------
CLOUD COMPUTE (life-sciences-cloud)
--------------------------------------------------------------------------------

Test 13: "Submit an AWS Batch job using job definition 'variant-calling-job'
          on queue 'genomics-queue' with parameters {sample: 'NA12878'}, then
          check its status"
Expected: Batch submit returns job ID → status query returns RUNNING/SUCCEEDED

Test 14: "List my Terra workspaces, then submit a workflow to workspace
          'my-genomics-workspace' using method 'gatk-germline'"
Expected: Lists workspaces → submits workflow → returns submission ID

Test 15: "Find the BWA-MEM tool on Galaxy (usegalaxy.org), then submit a job
          with my FASTQ files as input"
Expected: Galaxy tool search → finds BWA-MEM → submits job → returns job ID

--------------------------------------------------------------------------------
DATA VALIDATION (life-sciences-datastandards)
--------------------------------------------------------------------------------

Test 16: "Validate this SBML model file for correctness against SBML Level 3
          Version 2, then parse it and show me the compartments, species, and
          reactions"
Expected: SBML validation returns errors/warnings → parse returns structured
          model components

Test 17: "Validate my ISA-Tab investigation file and check if it meets MINSEQE
          compliance requirements"
Expected: ISA-Tab validation → compliance checklist assessment

Test 18: "Parse this BioPAX pathway file and show me the pathways,
          interactions, and physical entities"
Expected: BioPAX parse returns structured pathway components

--------------------------------------------------------------------------------
CLINICAL DATA INTEGRATION (life-sciences-healthcare)
--------------------------------------------------------------------------------

Test 19: "Connect to my FHIR server, search for all Patient resources with
          condition 'diabetes', then create a new Observation resource for
          patient P001 with HbA1c value 7.2%"
Expected: FHIR search returns patients → FHIR create submits new
          Observation → returns resource ID and version

Test 20: "Parse this HL7 v2 ADT^A01 message, extract the patient demographics,
          then generate a new HL7 message with updated address"
Expected: HL7 parse → structured segments → HL7 generate with modifications

Test 21: "Export all records from my REDCap project (ID: 12345) in JSON format,
          then map the key fields to OMOP CDM concepts"
Expected: REDCap export → data in JSON → OMOP concept mapping suggestions

--------------------------------------------------------------------------------
AI/ML INFERENCE (life-sciences-aiml)
--------------------------------------------------------------------------------

Test 22: "Get ESM protein embeddings for the sequence MEEPQSDPSVEPPLSQETFS,
          predict its secondary structure, and generate a contact map"
Expected: ESM returns per-residue embeddings, secondary structure predictions
          (helix/sheet/coil), and predicted contact map

Test 23: "Submit this protein sequence for AlphaFold structure prediction,
          then check the job status"
Expected: AlphaFold submit returns job ID → status check returns progress
          and estimated completion time

Test 24: "Extract all biomedical entities from this abstract: 'Mutations in
          BRCA1 and BRCA2 significantly increase the risk of breast and
          ovarian cancer. Olaparib, a PARP inhibitor, shows efficacy in
          BRCA-mutated tumors.' Then answer: What drugs target BRCA-mutated
          cancers?"
Expected: Entity extraction → BRCA1 (gene), BRCA2 (gene), breast cancer
          (disease), ovarian cancer (disease), Olaparib (drug), PARP (protein)
          → QA returns "Olaparib" with confidence score

--------------------------------------------------------------------------------
MICROBIOME ANALYSIS (life-sciences-microbiology)
--------------------------------------------------------------------------------

Test 25: "Run a QIIME 2 diversity analysis on my 16S amplicon data, then
          search SILVA for the taxonomy of the top OTUs, and check CARD for
          any antibiotic resistance genes in the community"
Expected: QIIME 2 action → diversity results → SILVA taxonomy lookup →
          CARD resistance gene search

Test 26: "Search BV-BRC for Mycobacterium tuberculosis genomes, get the
          genomic features for the top result, then check CARD for resistance
          determinants"
Expected: BV-BRC genome search → features for genome → CARD analysis

--------------------------------------------------------------------------------
ECOLOGY WORKFLOWS (life-sciences-ecology)
--------------------------------------------------------------------------------

Test 27: "Search GBIF for all occurrences of Panthera tigris in India,
          get the IUCN conservation status, and find recent iNaturalist
          observations with photos"
Expected: GBIF occurrences with coordinates → IUCN Endangered status →
          iNaturalist observations with quality grades

Test 28: "Search MGnify for soil metagenome studies, then get the taxonomic
          summary for the top result"
Expected: MGnify study search → taxonomic composition data

--------------------------------------------------------------------------------
IMMUNOLOGY & VACCINE DESIGN (life-sciences-immunology)
--------------------------------------------------------------------------------

Test 29: "Search IEDB for T-cell epitopes from SARS-CoV-2 spike protein
          restricted to HLA-A*02:01, then analyze the top epitope sequence
          with abYsis for structural features"
Expected: IEDB epitope search with MHC restriction → abYsis sequence
          analysis with CDR annotations

--------------------------------------------------------------------------------
SINGLE-CELL ANALYSIS (life-sciences-cellbiology)
--------------------------------------------------------------------------------

Test 30: "Search CellxGene for single-cell datasets from human lung tissue,
          then get the expression of ACE2 across cell types in the top dataset"
Expected: CellxGene dataset search → expression query → ACE2 expression
          grouped by cell type with percentages
