---
inclusion: manual
---

# Immunology and Vaccine Design

Practical guidance for epitope prediction, MHC binding analysis, antibody engineering, and immunogenicity assessment.

## Epitope Prediction Workflows

### T-Cell Epitope Prediction
1. Obtain protein sequence of the target antigen.
2. Predict MHC class I binding peptides (8–11 mers) using NetMHCpan or IEDB tools.
3. Predict MHC class II binding peptides (13–25 mers) using NetMHCIIpan.
4. Filter by binding affinity (IC50 < 500 nM for strong binders, < 5000 nM for weak).
5. Predict proteasomal cleavage and TAP transport for MHC-I pathway.
6. Rank candidates by combined score.

### B-Cell Epitope Prediction
- **Linear epitopes**: Use BepiPred or ABCpred for sequence-based prediction.
- **Conformational epitopes**: Use DiscoTope or ElliPro with 3D structure.
- Surface accessibility and hydrophilicity are key predictors.

### Population Coverage
- Select epitopes covering multiple HLA alleles for broad population coverage.
- Use IEDB Population Coverage tool to estimate coverage across ethnic groups.
- Target > 90% population coverage for vaccine candidates.

## MHC Binding Analysis

### HLA Allele Selection
- Focus on the most frequent alleles: HLA-A*02:01, HLA-A*01:01, HLA-B*07:02, etc.
- Use allele frequency data from the Allele Frequency Net Database.
- Include at least 12 HLA-I and 12 HLA-II alleles for broad coverage.

### Binding Prediction Tools
| Tool | Type | Method | Access |
|------|------|--------|--------|
| NetMHCpan | MHC-I | Neural network | IEDB |
| NetMHCIIpan | MHC-II | Neural network | IEDB |
| MHCflurry | MHC-I | Deep learning | Python package |
| IEDB Consensus | Both | Ensemble | IEDB web/API |

### Interpreting Results
- **IC50 < 50 nM**: Strong binder (high confidence).
- **IC50 50–500 nM**: Moderate binder (good candidate).
- **IC50 500–5000 nM**: Weak binder (consider if other evidence supports).
- **Percentile rank < 2%**: Strong binder relative to random peptides.

## Antibody Engineering Patterns

### Antibody Structure
- **Variable regions (Fv)**: Antigen-binding site with 6 CDR loops (3 from VH, 3 from VL).
- **Framework regions (FR)**: Structural scaffold supporting CDR loops.
- **Constant regions**: Effector function (IgG1, IgG2, IgG4 subtypes).

### Humanization Strategies
- **CDR grafting**: Transplant CDRs from donor antibody onto human framework.
- **Back-mutations**: Restore key framework residues that affect CDR conformation.
- **Resurfacing**: Replace only surface-exposed non-human residues.

### Affinity Maturation
- Identify hotspot residues in CDRs using alanine scanning.
- Generate focused libraries with NNK codons at hotspot positions.
- Screen by phage display, yeast display, or mammalian display.

### Numbering Schemes
- **Kabat**: Based on sequence variability. Standard for CDR definition.
- **Chothia**: Based on structural loops. Better for structural analysis.
- **IMGT**: International standard. Consistent across species.
- Use abYsis or ANARCI for automatic numbering.

## Immunogenicity Assessment

### In Silico Prediction
- Predict T-cell epitopes in the therapeutic protein sequence.
- Identify "immunogenic hotspots" with clusters of predicted epitopes.
- Compare to human proteome to identify non-self peptides.

### De-immunization Strategies
- Mutate anchor residues in predicted epitopes to reduce MHC binding.
- Verify mutations do not affect protein function or stability.
- Validate with in vitro T-cell assays (ELISpot, proliferation).

### Risk Factors
- Non-human sequences (chimeric antibodies) → higher risk.
- Aggregation-prone formulations → higher risk.
- Subcutaneous administration → higher risk than IV.
- Patient immune status (immunocompromised → lower risk).

## Tools and Resources
- **IEDB**: Immune Epitope Database — epitope prediction and analysis tools.
- **IMGT**: International ImMunoGeneTics — antibody sequence and structure data.
- **abYsis**: Antibody numbering and structure analysis.
- **ImmPort**: Shared data repository for immunology research.
- Use the immunology MCP server for programmatic access to IEDB, IMGT, ImmPort, and abYsis.
