---
inclusion: auto
---

# Resource Catalog Browsing

Step-by-step guide to discover, search, and browse the life sciences resource catalog.

## Step 1: View Available Categories

1. Get all resource categories with counts:
   - Use the resource catalog `getCategories()` function.
2. Review the 25 categories: Genomics, Proteomics, Structural Biology, Clinical, Ecology, etc.
3. Identify categories relevant to your research area.

## Step 2: Browse by Category

1. Select a category to explore:
   - Use `browse(category)` to list all resources in that category.
2. Resources are sorted alphabetically by name.
3. Review each resource's status: `ready`, `needs_setup`, or `needs_credentials`.

## Step 3: Search by Keyword

1. Search across all resources:
   - Use `search(keyword)` with a term like "variant", "protein", or "FASTA".
2. Results are ranked by relevance:
   - Exact name match (highest).
   - Name contains keyword.
   - Description contains keyword.
   - Category matches keyword.
   - Data formats contain keyword (lowest).

## Step 4: Filter Results

1. Apply filters to narrow results:
   - **Category**: e.g., "Genomics and Sequencing".
   - **Resource type**: "database", "pipeline", "tool", "skill", or "steering_file".
   - **Auth requirement**: "authenticated" or "open_access".
2. Combine filters for precise results.

## Step 5: View Resource Details

1. Select a resource to view full metadata:
   - Use `getEntry(id)` for complete details.
2. Review: description, API base URL, rate limits, data formats, usage instructions.
3. Check authentication requirements and credential setup instructions.

## Step 6: Explore Related Resources

1. View resources commonly used together:
   - Use `getRelated(id)` to find cross-referenced resources.
2. Follow cross-references to discover complementary databases and tools.

## Expected Outputs
- List of available resources matching your research needs.
- Setup instructions for resources that need configuration.
- Cross-references to related resources for comprehensive workflows.
