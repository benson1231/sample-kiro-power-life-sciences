---
inclusion: auto
fileMatchPattern: "**/*primer*,**/*clone*,**/*restriction*,**/*plasmid*"
---

# Primer Design and Cloning

Step-by-step guide for primer design, specificity checking, and cloning strategy using Primer3, PrimerBLAST, and REBASE.

## Step 1: Design Primers with Primer3

1. Submit target sequence for primer design:
   - Use `life-sciences-molbio` → `primer3_design` tool.
2. Set parameters:
   - Product size range: 100–300 bp (for qPCR) or 500–3000 bp (for cloning).
   - Tm range: 58–62°C (optimal 60°C).
   - GC content: 40–60%.
   - Max self-complementarity: 4.
3. Review returned primer pairs with Tm, GC%, and penalty scores.

## Step 2: Check Specificity with PrimerBLAST

1. Validate primer specificity:
   - Use `life-sciences-molbio` → `primerblast_check` tool with primer sequences.
2. Select the target organism genome for specificity checking.
3. Review off-target amplification products.
4. Reject primers with significant off-target hits.

## Step 3: Find Restriction Sites with REBASE

1. Search for restriction enzymes compatible with your cloning vector:
   - Use `life-sciences-molbio` → `rebase_search` tool.
2. Check that selected enzymes do not cut within your insert sequence:
   - Use `life-sciences-molbio` → `restriction_analysis` tool.
3. Select enzyme pair for directional cloning (e.g., EcoRI + BamHI).

## Step 4: Design Cloning Strategy

1. Add restriction sites to primer 5' ends:
   - Forward primer: 5'-[overhang]-[RE site]-[target sequence]-3'
   - Reverse primer: 5'-[overhang]-[RE site]-[target sequence]-3'
2. Include 4–6 nt overhang before restriction site for efficient cutting.
3. Verify reading frame is maintained for fusion constructs.

## Step 5: Validate In Silico

1. Simulate restriction digest of the final construct:
   - Use `life-sciences-molbio` → `restriction_analysis` tool.
2. Verify expected fragment sizes match the design.
3. Check for internal restriction sites that could cause problems.

## Expected Outputs
- Optimized primer pair with Tm, GC%, and specificity report.
- Restriction enzyme selection for cloning.
- Complete cloning strategy with primer sequences including RE sites.
- In silico digest validation with expected fragment sizes.
