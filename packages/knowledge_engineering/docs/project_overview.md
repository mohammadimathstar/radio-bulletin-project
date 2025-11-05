# Knowledge Graph Construction Project – Overview

## 1. Project Scope

This project aims to **extract structured entities and relations from radio bulletins** and build a **Knowledge Graph (KG)** that integrates:

- **Entities** such as people, organizations, locations, publications, events, and artifacts.
- **Relations** between entities, both factual attributes (e.g., nationality, location) and semantic relations extracted by an LLM.
- **External knowledge enrichment** via Wikidata linking.

The resulting KG can be exported for visualization or imported into graph databases like **Neo4j** for querying and analysis.

---

## 2. Entity Ontology

The project defines a **typed entity schema** that ensures consistency and enables semantic linking. Each entity type has attributes for identification, description, and provenance.

### 2.1 Base Entity

All entities inherit from a `BaseEntity` with core fields:

- `id`: Unique identifier for the entity in the bulletin.
- `name`: Exact text mention of the entity.
- `description`: Optional summary extracted from text.
- `text_span`: Exact text snippet containing the enti
- `context_sentence`: Optional sentence from which the entity is extracted.

---

### 2.2 Specific Entities

| Entity Type | Key Fields | Description |
|-------------|------------|-------------|
| **Person** | `inferred_full_name`, `nationality`, `occupation`, `gender` | Represents individuals mentioned in bulletins. |
| **Organization** | `official_name`, `org_type`, `location` | Companies, political parties, NGOs, etc. |
| **Location** | `location_type`, `country` | Geographic entities (city, country, region). |
| **Publication** | `title`, `publisher`, `date_time`, `type` | Newspapers, journals, or other publications. |
| **Event** | `event_type`, `start_date`, `end_date`, `participants`, `location` | Historical or political events mentioned in bulletins. |
| **Artifact** | `artifact_type`, `creation_date` | Objects, treaties, laws, or other historical artifacts. |

---

### 2.3 Relations

Relations between entities are captured in two categories:

1. **Factual Relations** – derived from entity attributes (stored as edges in the KG). Examples:

- `HAS_NATIONALITY`: Person → Country
- `HAS_OCCUPATION`: Person → Occupation
- `LOCATED_IN`: Organization → Location

2. **LLM-Extracted Semantic Relations** – extracted from bulletin text using language models. Examples:

- `member_of`, `located_in`, `participated_in`
- `gave_speech`, `authored`, `signed`, `produced`
- `published`, `part_of`, `caused`, `opposed`, `supported`
- `reported_on`, `affected`, `succeeded_by`, `preceded_by`, `supervised_by`

Each relation optionally includes a **certainty score** (0–1) indicating model confidence.

---

## 3. Pipeline Overview

The pipeline consists of **four major stages**:

### 3.1 Entity Extraction

- Extracts structured entities from bulletins using a combination of NLP and LLMs.
- Populates fields according to the **ontology**.
- Each bulletin is stored as a `BulletinExtraction` object containing entities and relations.

### 3.2 Entity Linking

- Entities are **linked to Wikidata** to enrich metadata.
- Supports:
  - **Semantic similarity** using sentence embeddings
- Adds the following Wikidata metadata:
  - `wikidata_id`, `wikidata_uri`, `wikidata_label`, `wikidata_description`
  - `api_match_score`, `similarity_score`

### 3.3 Knowledge Graph Construction

- Builds a **typed property graph** (`networkx.MultiDiGraph`) integrating:
  - Entities as nodes with metadata
  - Factual relations as edges
  - LLM-extracted semantic relations as edges
- Special handling:
  - Event participants are linked to existing person/organization nodes
  - Locations are typed as `Location` instead of generic `Concept`
  - Node attributes are merged if an entity appears in multiple bulletins
- Output can be saved as **GraphML** for Neo4j import.

### 3.4 Neo4j Upload

- Uses `Neo4jUploader` to:
  - Clear or preserve existing database
  - Create unique constraints
  - Upload nodes with labels and properties
  - Upload edges with relation types and attributes

---

## 4. Data Flow

```
Raw Bulletins (Text)
        │
        ▼
Entity Extraction → Structured CSVs per entity type
        │
        ▼
Wikidata Linking → Enriched entities with global IDs
        │
        ▼
KG Construction → Nodes (entities), Edges (relations)
        │
        ▼
Neo4j Upload → Queryable Knowledge Graph
```

---

## 5. Features & Highlights

- **Structured Ontology** ensures standardization across bulletins.
- **Factual + Semantic Relations** allow both attribute-based and context-based reasoning.
- **Wikidata Integration** links local entities to global identifiers.
- **GraphML & Neo4j Support** enables advanced graph queries and visualization.
- **Caching & Batch Processing** optimize repeated runs and large datasets.

---

## 6. Intended Use

- Historical or political bulletin analysis
- Social network mapping of individuals and organizations
- Event tracking and timeline reconstruction
- Knowledge integration for research and intelligence applications

---

This file provides a **high-level understanding** of the project, its ontology, pipel
