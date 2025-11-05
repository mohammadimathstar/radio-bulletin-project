# Step 3: Entity Linking to Wikidata

## Overview

This module links extracted entities (people, organizations, locations, events, publications, artifacts) to their corresponding **Wikidata URIs**. It supports both:

- **Fuzzy string matching** using `rapidfuzz`
- **Semantic similarity** using `sentence-transformers` embeddings

The purpose is to enrich your structured entities with global identifiers, descriptions, and metadata for downstream knowledge graph construction and analysis.

---

## Workflow

### 1. Search Wikidata for Candidate Entities
- Uses the Wikidata API endpoint `wbsearchentities`.
- Returns a list of candidate entities with:
  - Labels
  - Descriptions
  - API match scores

### 2. Match Candidates to the Entity
- Optional description columns (e.g., nationality, occupation, type) are used for disambiguation.
- Two matching methods:
  - `"fuzzy"`: Character-level partial similarity
  - `"semantic"`: Cosine similarity between sentence embeddings

### 3. Batch Linking for a DataFrame
- Enriches input DataFrame with new columns:
  - `wikidata_id`: Wikidata QID
  - `wikidata_uri`: URL to the Wikidata entity
  - `wikidata_label`: Label of matched entity
  - `wikidata_description`: Wikidata description
  - `api_match_score`: Score from the Wikidata API
  - `similarity_score`: Similarity score between entity description and Wikidata description
- Supports caching results to avoid repeated API calls
- Optionally appends extra columns (e.g., nationality, occupation) to improve matching

---

## Key Functions

### `search_wikidata_entity(name, language='en', limit=10)`
- Wrapper for the Wikidata API to retrieve candidate entities for a given name.
- Retries up to 3 times on network or JSON errors.

### `fuzzy_similarity(desc1, desc2)` / `semantic_similarity(desc1, desc2)`
- Computes similarity between two descriptions.
- `fuzzy_similarity`: Partial string match
- `semantic_similarity`: Sentence embeddings + cosine similarity

### `match_entity_to_wikidata(name, description=None, matching_method='fuzzy', ...)`
- Finds the most likely Wikidata entity for a given name and optional description.
- Returns a dictionary containing:
  - `wikidata_id`, `wikidata_uri`, `wikidata_label`, `wikidata_description`
  - `api_match_score`, `similarity_score`
- Defaults to the top API candidate if no description is provided.

### `link_entities_to_wikidata(df, entity_type, col_name='canonical_name', description_col=None, added_cols=None, ...)`
- Batch links all entities in a DataFrame to Wikidata.
- Enriches descriptions with additional columns for better matching.
- Caches results for faster repeated runs.
- Optionally saves enriched DataFrame to a file.

### `link_all_entities_to_wikidata(input_dir, name_col='cluster_rep', description_col='description', ...)`
- Orchestrates linking for all entity types:
  - person, organization, location, publication, event, artifact
- Reads pre-clustered CSVs from `input_dir/clustered/`.
- Writes enriched files to `input_dir/enriched_wikidata/<matching_method>/`.
- Returns a dictionary of enriched DataFrames for all entity types.

---

## Usage Example

```python
from wikidata_search import link_all_entities_to_wikidata

# Link all entity types in a folder
entity_dfs = link_all_entities_to_wikidata(
    input_dir="./data/structured_data",
    name_col="cluster_rep",
    description_col="description",
    matching_method="semantic",
    language="en",
    limit=10,
    verbose=True
)

# Access linked people
people_df = entity_dfs['person']
```

---

## Notes / Best Practices

- **Caching:** Stores results in `wikidata_cache.json` to avoid repeated queries.
- **Additional columns:** Attributes like `nationality`, `occupation`, or `org_type` can be added to descriptions for better disambiguation.
- **People name check:** Skips names with fewer than two words to reduce ambiguity.
- **Rate limiting:** Use `sleep_time` to avoid hitting Wikidata API limits.
- **Similarity methods:** Semantic similarity performs better with rich descriptions; fuzzy matching is faster.
- **Extensibility:** Add new entity types by extending `ADDED_COLS_TO_DESCRIPTION` and providing corresponding CSV files.

---

## Output

- Enriched CSVs with Wikidata metadata for each entity type:
  - `persons.csv`, `organizations.csv`, `locations.csv`, `publications.csv`, `events.csv`, `artifacts.csv`
- Cached JSON file for