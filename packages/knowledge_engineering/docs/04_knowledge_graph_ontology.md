# Knowledge Graph Construction, Ontology & Neo4j Upload

## Overview

This module builds a **Knowledge Graph (KG)** from clustered entity CSVs and LLM-extracted relations, capturing both factual and semantic connections between entities.  

It supports:

- **Entities (nodes)**: Person, Organization, Event, Location, Publication, Artifact, Bulletin.
- **Relations (edges)**:
  - **Factual relations** (attribute-based)
  - **Semantic relations** (LLM-extracted)
- **Graph export**: GraphML for Neo4j or direct upload using `Neo4jUploader`.

---

## Ontology

### Entity Types

| Entity | Key Fields | Description |
|--------|------------|-------------|
| **Person** | id, name, inferred_full_name, occupation, nationality, gender | Individuals mentioned in text. |
| **Organization** | id, name, official_name, org_type, location | Companies, political parties, institutions. |
| **Location** | id, name, location_type, country | Geographic entities (city, country, region). |
| **Publication** | id, title, publisher, date_time, type | Newspapers, journals, reports. |
| **Event** | id, name, event_type, start_date, end_date, location, participants | Political, social, or cultural events. |
| **Artifact** | id, name, artifact_type, creation_date | Tangible items (laws, treaties, ships). |
| **Bulletin** | bulletin_id, transcript, bulletin_topic, bulletin_summary | Top-level container for extracted entities. |

### Node Labeling

- Node labels correspond to entity type (capitalized): `Person`, `Organization`, `Location`, `Event`, `Publication`, `Artifact`, `Bulletin`.
- Metadata fields are stored as node properties.
- `id` is unique per node type; enforced as Neo4j constraint.

---

### Factual Relations

These are attribute-based and defined in `ENTITY_CONFIG`:

| Entity | Relation | Edge Label | Target Type |
|--------|---------|-----------|------------|
| Person | occupation | `HAS_OCCUPATION` | Concept |
| Person | nationality | `HAS_NATIONALITY` | Concept |
| Person | gender | `HAS_GENDER` | Concept |
| Person | entity_type | `IS_INSTANCE_OF` | Concept |
| Organization | org_type | `HAS_ORGANIZATION_TYPE` | Concept |
| Organization | location | `LOCATED_IN` | Location |
| Organization | entity_type | `IS_INSTANCE_OF` | Concept |
| Event | participants | `HAS_PARTICIPANT` | Person/Organization |
| Event | location | `OCCURRED_IN` | Location |
| Event | event_type | `HAS_EVENT_TYPE` | Concept |
| Event | entity_type | `IS_INSTANCE_OF` | Concept |
| Artifact | artifact_type | `HAS_ARTIFACT_TYPE` | Concept |
| Artifact | entity_type | `IS_INSTANCE_OF` | Concept |
| Publication | type | `HAS_PUBLICATION_TYPE` | Concept |
| Publication | publisher | `PUBLISHED_BY` | Organization |
| Publication | entity_type | `IS_INSTANCE_OF` | Concept |

**Special handling rules**:

- Participants are linked to existing `Person`/`Organization` nodes.
- Location and country fields create `Location` nodes.
- Attributes are merged if multiple occurrences exist.

---

### LLM-extracted Semantic Relations

These represent interactions or connections detected in text:

```text
member_of, located_in, participated_in, occurred_at, gave_speech,
authored, signed, produced, published, part_of, caused,
opposed, supported, reported_on, affected, succeeded_by,
preceded_by, supervised_by
```

- Stored as edges in the KG.
- Attributes include `source="LLM"`, `bulletin_id`, and optional `certainty`.

---

## Workflow

1. **Load entities**
   - CSVs or `BulletinExtraction` objects → nodes with metadata and labels.

2. **Add factual relations**
   - From `ENTITY_CONFIG.factual_relations`.
   - Participants and location/country handled specially.

3. **Add semantic relations**
   - Read relations CSV extracted by LLM.
   - Create edges with `relation_type` and optional certainty.

4. **Build KG**
   - Combine nodes and edges into `networkx.MultiDiGraph`.
   - Optional provenance linking: `MENTIONED_IN` edges from entities to bulletins.
   - Optional GraphML export.

5. **Upload to Neo4j**
   - Clear database (optional) and create uniqueness constraints.
   - Upload nodes and edges, preserving labels and properties.

---

## Example Usage

```python
from build_kg import build_knowledge_graph, ENTITY_CONFIG
from neo4j_uploader import Neo4jUploader

# Build KG
G = build_knowledge_graph(
    entities_dir="data/entities",
    relations_file="data/relations.csv",
    save_graphml="data/kg.graphml"
)

print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

# Upload to Neo4j
uploader = Neo4jUploader(uri="bolt://localhost:7687", user="neo4j", password="password")
uploader.upload_graph(G, clear_first=True)
uploader.close()
```

---

## Notes

- Node/edge labels are Neo4j-friendly (`capitalize` nodes, uppercased relations).
- Factual edges vs LLM edges are distinguished (`source="FACTUAL"` vs `"LLM"`).
- Deduplication is applied to nodes; attributes merged with `;`.
- Confidence scores (`certainty`) preserved for semantic relations.
- Ontology provides a structured, consistent schema for querying KG in Neo4j.

