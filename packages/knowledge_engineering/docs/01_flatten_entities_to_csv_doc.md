# 🧩 Step 1 — Flattening JSONL Bulletins into Structured CSVs

## Overview

This step transforms **semi-structured JSONL bulletins** (produced by OCR or LLM extraction) into **flat, relational CSV tables** — one per entity type (`persons`, `organizations`, `events`, `locations`, etc.).

The goal is to **normalize deeply nested JSON data** into a **consistent tabular structure** that can serve as input for later stages such as **entity resolution, enrichment, and knowledge graph construction**.

---

## 🎯 Objectives

- Parse and flatten nested fields inside `raw_output` of each bulletin.
- Assign **globally unique identifiers** to all entities (`bulletin_id + local_id`).
- Normalize field names and values (canonical names, type-safe lists, etc.).
- Handle **cross-entity relations** by linking sources and targets via global IDs.
- Export clean CSVs under `data/entities/` for downstream processing.

---

## 🧠 Conceptual Flow

```text
raw_bulletins.jsonl
       │
       ▼
 [Read JSON Lines]
       │
       ▼
 [Flatten entities by type]
       │
       ├── persons.csv
       ├── organizations.csv
       ├── locations.csv
       ├── events.csv
       ├── publications.csv
       ├── artifacts.csv
       ├── relations.csv
       └── bulletins.csv
```

Each entity type becomes a table, linked together by **global entity IDs** and **bulletin IDs**.

---

## ⚙️ Configuration

### Preferred Fields

Defines which key to use as the canonical name per entity type:

```python
PREFERRED_FIELDS = {
    "people": "inferred_full_name",
    "organizations": "official_name",
    "publications": "title",
    "events": "name",
    "locations": "name",
    "artifacts": "name",
}
```

### Entity Types

Specifies which tables to create:

```python
ENTITY_TYPES = [
    "bulletins", "persons", "organizations", 
    "locations", "publications", 
    "artifacts", "events", "relations"
]
```

---

## 🧩 Core Functions

### 1. `safe_list(x)`
Guarantees a value is returned as a list, handling strings, singletons, and malformed literals.

Useful when entity fields may contain either a list or a single string.

---

### 2. `canonical_name(ent, etype)`
Returns the **canonical name** for an entity, prioritizing `PREFERRED_FIELDS[etype]` or defaulting to `"name"`.  
Ensures consistency when entities have multiple name-like attributes.

---

### 3. `flatten_entity_type(bulletin_id, etype, entities, entity_lookup)`
Flattens a list of entities of a specific type.

#### Responsibilities:
- Generates **unique IDs** (`<bulletin_id>_<local_id>`).
- Adds `canonical_name` and `bulletin_id`.
- Handles **event participants**:
  - Converts local participant IDs to **global IDs**.
  - Stores both `participants_global` and human-readable `participants_label`.
- Updates `entity_lookup` for later cross-referencing.

#### Example:
```python
{
  "bulletin_id": "B123",
  "raw_entity_id": "B123_4",
  "canonical_name": "UNESCO",
  "entity_type": "organization"
}
```

---

### 4. `flatten_relations(bulletin_id, relations, entity_lookup)`
Converts raw relation records into flat rows linking source and target entities.

#### Key steps:
- Skips incomplete relations (missing source or target).
- Maps both ends (`source_id`, `target_id`) to **global entity IDs** and **labels**.
- Adds relation metadata (e.g., `relation_type`, `certainty`).

#### Example output row:
| bulletin_id | source_id | target_id | source_label | target_label | relation_type |
|--------------|------------|------------|---------------|---------------|----------------|
| B123 | B123_4 | B123_9 | UNESCO | Paris | LOCATED_IN |

---

### 5. `flatten_entities(data, field="raw_output")`
Main orchestration function.

#### Workflow:
1. Initialize `entity_dfs` (one list per entity type).
2. Iterate through bulletins:
   - Add a `bulletins` record with metadata.
   - Flatten entities for each type.
   - Flatten relations using `entity_lookup`.
3. Convert all lists into **pandas DataFrames**.

Returns:
```python
{
    "persons": pd.DataFrame(...),
    "organizations": pd.DataFrame(...),
    "events": pd.DataFrame(...),
    "relations": pd.DataFrame(...),
    ...
}
```

---

## 🧾 Example Usage

```python
import json
from flatten_entities_to_csv import flatten_entities

# Load structured JSONL file
with open("data/raw_bulletins.jsonl", "r") as f:
    data = [json.loads(line) for line in f]

# Flatten to DataFrames
entity_dfs = flatten_entities(data)

# Save each entity type
for etype, df in entity_dfs.items():
    df.to_csv(f"data/entities/{etype}.csv", index=False)
```

---

## 🧱 Output Structure

Example generated files under `data/entities/`:

| File | Description |
|------|--------------|
| `bulletins.csv` | Metadata per bulletin (text, topic, summary) |
| `persons.csv` | All person entities |
| `organizations.csv` | All organization entities |
| `locations.csv` | Location entities |
| `publications.csv` | Publication entities |
| `artifacts.csv` | Artifact entities |
| `events.csv` | Event entities (with participant IDs) |
| `relations.csv` | Links between entities |

---

## 🧭 Design Principles

- **Traceability:** Every entity and relation maintains a clear link to its originating bulletin.  
- **Reproducibility:** Outputs are deterministic given the same JSONL input.  
- **Extensibility:** Adding new entity types or canonical fields only requires updating configuration constants.  
- **Fault-tolerant:** Invalid or incomplete records are skipped gracefully with warnings.  
- **Transparency:** Verbose logging for skipped or malformed entities/relations.

---

## 🧩 Next Step

The flattened CSVs become the **input** for the next pipeline stage:
> **Step 2 — Entity Resolution and Clustering**  
> (`ent