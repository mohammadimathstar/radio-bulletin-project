# Entity Resolution and Clustering

## Overview

This module (`clustering_entities.py`) performs **entity resolution** by clustering extracted entity names (people, organizations, publications, locations, etc.) based on string similarity. It also allows optional secondary filtering attributes (like nationality, occupation, or type) to ensure entities in the same cluster share certain properties.

The goal is to produce a consistent set of canonical names (`cluster_rep`) and cluster IDs (`cluster_id`) for downstream knowledge graph construction.

---

## Workflow

1. **Normalization**
   - All entity names are normalized (lowercased, accents removed, whitespace cleaned) before similarity computation.

2. **Compute Similarity**
   - Pairwise similarity between entity names is computed using the `rapidfuzz` library.
   - Similarity scores are on a 0–100 scale.

3. **Hierarchical Clustering**
   - Converts similarity to distance (0–1 scale) and performs hierarchical clustering.
   - Clusters are assigned based on a `distance_threshold`.

4. **Representative Name Selection**
   - Within each cluster, the longest name is selected as the representative (`cluster_rep`).

5. **Optional Filtering**
   - Entities can be grouped by additional attributes (`filter_cols`) before clustering to ensure semantic consistency.

6. **Unclustered Handling**
   - Entities with missing filter values are compared against existing clusters.
   - If similarity is above the threshold, they are merged; otherwise, a new cluster is created.

7. **Output**
   - Saves clustered results to CSV files (`<entity_type>s.csv`) including `cluster_id` and `cluster_rep`.

---

## Key Functions

### `hierarchical_clustering(sim_matrix, distance_threshold)`
- Performs hierarchical clustering on a similarity matrix.
- Returns cluster IDs and linkage matrices.

### `pick_longest_name(series)`
- Helper function to select the longest name in a cluster.

### `cluster_entities(df, col_name, distance_threshold, filter_cols)`
- Clusters entity names in a DataFrame with optional secondary filtering.
- Returns:
  - DataFrame with `cluster_id` and `cluster_rep`
  - Array of cluster IDs
  - List of linkage matrices

### `assign_unclustered(unclustered_df, clustered_df, col_name, distance_threshold)`
- Assigns unclustered entities into existing clusters if sufficiently similar.
- Otherwise, assigns a new cluster.

### `cluster_and_save(df, entity_type, col_name, filter_col, distance_threshold, output_dir)`
- Convenience function to cluster entities and save results as CSV.

---

## Dependencies

- `pandas`
- `numpy`
- `scipy` (hierarchy, spatial.distance)
- `rapidfuzz` (string similarity)
- `matplotlib` (optional dendrogram visualization)
- `pathlib`
- `collections`
- `src.io_utils.load_entity_data`
- `src.entity_resolution.str_utils.normalize_name, compute_similarity_matrix`
- `src.entity_resolution.dutch_to_english.DUTCH_TO_ENGLISH`

---

## Usage Example

```python
from clustering_entities import cluster_and_save
from src.io_utils import load_entity_data

# Load entity dataframe
df_people = load_entity_data(entity_type="people", data_dir="./data/entities")

# Cluster people using optional filter (e.g., nationality)
clustered_df, linkages = cluster_and_save(
    df_people,
    entity_type="person",
    col_name="canonical_name",
    filter_col=["nationality"],
    distance_threshold=0.15,
    output_dir="./data/entities"
)

# Access cluster IDs and representative names
print(clustered_df[["canonical_name", "cluster_id", "cluster_rep"]].head())
```

---

## Notes

- **Filtering**: Ensures semantic consistency within clusters.
- **Single-element groups**: Assigned a unique cluster ID.
- **Unclustered entities**: Compared with existing clusters and merged if similarity exceeds the threshold.
- **Normalization**: Improves string similarity and reduces duplicates.
- **Representative names**: Longest name in a cluster is chosen for consistency.
- **Designed for downstream KG construction**: Provides clean, disambiguated entities for knowledg