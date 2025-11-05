import pandas as pd
import ast
from pathlib import Path
from src.data_loader import read_jsonl

# --- Configuration ---

PREFERRED_FIELDS = {
    "people": "inferred_full_name",
    "organizations": "official_name",
    "publications": "title",
    "events": "name",
    "locations": "name",
}

ENTITY_TYPES = ["people", "organizations", 
                "locations", "publications", 
                "artifacts", "events", "relations"]
# RELATION_TYPES = ["relations"]


def flatten_entities(data, field: str = "raw_output"):
    """
    Flatten entities and relations from all bulletins.
    Adds raw_entity_id, canonical_name, and global entity tracking.
    Handles missing or noisy relations.
    """
    entity_dfs = {etype: [] for etype in ENTITY_TYPES}
    entity_lookup = {}  # key: raw_entity_id -> canonical_name

    for doc in data:
        bulletin_id = doc.get("id", "UNKNOWN_BULLETIN")
        parsed = doc.get(field) or {}

        # --- Entities ---
        for etype in ENTITY_TYPES:
            if etype == "relations":
                continue

            entities = parsed.get(etype, [])
            for ent in entities:
                if not isinstance(ent, dict):
                    print(f"⚠️ Skipping invalid {etype} in bulletin {bulletin_id}: not a dict")
                    continue

                local_id = ent.get("id")
                # Unique ID across bulletins
                raw_entity_id = f"{bulletin_id}_{local_id}" if local_id else None

                # canonical candidate (for clustering)
                display_field = PREFERRED_FIELDS.get(etype)
                canonical = ent.get(display_field) or ent.get("name") or f"{local_id}"

                ent.update({
                    "raw_entity_id": raw_entity_id,
                    "bulletin_id": bulletin_id,
                    "canonical_name": canonical,
                })

                # --- Handle participants for events ---
                if etype == "events" and "participants" in ent:
                    participants = ent.get("participants", [])
                    participants_global = []
                    participants_label = []

                    if isinstance(participants, str):
                        try:
                            parsed_participants = ast.literal_eval(participants)
                            if isinstance(parsed_participants, list):
                                values = parsed_participants
                            else:
                                values = [str(parsed_participants)]
                        except (SyntaxError, ValueError):
                            values = [participants]
                    elif isinstance(participants, list):
                        values = participants
                    else:
                        values = [participants]

                    for pid in values:
                        pid_global = f"{bulletin_id}_{pid}"
                        participants_global.append(pid_global)

                        if pid_global in entity_lookup:
                            participants_label.append(entity_lookup[pid_global])
                        else:
                            print(f"⚠️ Participant '{pid_global}' not found in bulletin {bulletin_id}")
                            participants_label.append(f"[MISSING:{pid_global}]")

                    ent["participants_global"] = participants_global
                    ent["participants_label"] = participants_label
                entity_dfs[etype].append(ent)

                if raw_entity_id:
                    entity_lookup[raw_entity_id] = canonical
        
        # --- Relations ---
        relations = parsed.get("relations", [])
        for rel in relations:
            if not isinstance(rel, dict):
                print(f"⚠️ Skipping invalid relation in {bulletin_id}: not a dict")
                continue

            src_local = rel.get("source_id")
            tgt_local = rel.get("target_id")

            if not src_local or not tgt_local:
                print(f"⚠️ Missing source/target in relation (bulletin {bulletin_id}): {rel}")
                continue

            src_global = f"{bulletin_id}_{src_local}"
            tgt_global = f"{bulletin_id}_{tgt_local}"

            if src_global not in entity_lookup:
                print(f"⚠️ Missing source entity '{src_global}' in bulletin {bulletin_id}")
                continue
            if tgt_global not in entity_lookup:
                print(f"⚠️ Missing target entity '{tgt_global}' in bulletin {bulletin_id}")
                continue

            rel_row = {
                "bulletin_id": bulletin_id,
                "source_id": src_global,
                "target_id": tgt_global,
                "source_label": entity_lookup.get(src_global, f"[MISSING:{src_global}]"),
                "target_label": entity_lookup.get(tgt_global, f"[MISSING:{tgt_global}]"),
                "relation_type": rel.get("relation_type"),
                "certainty": rel.get("certainty"),
            }
            entity_dfs["relations"].append(rel_row)

    # Convert lists to DataFrames
    entity_dfs = {k: pd.DataFrame(v) for k, v in entity_dfs.items()}
    return entity_dfs


def save_entity_csvs(entity_dfs, out_dir="data/entities"):
    """Save each entity type DataFrame to a separate CSV."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for etype, df in entity_dfs.items():
        if not df.empty:
            out_path = Path(out_dir) / f"{etype}.csv"
            df.to_csv(out_path, index=False)
            print(f"✅ Saved {etype}: {len(df)} rows → {out_path}")
        else:
            print(f"⚠️ Skipped {etype}: no entities found")


def load_entity_data(entity_type: str = "people", data_dir: str = "./data/entities/") -> pd.DataFrame:
    """
    Load entity data from a CSV file.
    Args:
        entity_type (str): The type of entity to load (default: "people").
        data_dir (str): Directory containing the CSV files.
    Returns:
        pd.DataFrame: DataFrame containing entity data with columns including 'name'.
    """
    file_path = Path(data_dir) / f"{entity_type}.csv"
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} entities of type '{entity_type}'.")
    return df


if __name__ == "__main__":
    input_file = "data/outputs/run1.jsonl"  # path to your LLM output
    data = read_jsonl(input_file)

    entity_dfs = flatten_entities(data)
    save_entity_csvs(entity_dfs)
