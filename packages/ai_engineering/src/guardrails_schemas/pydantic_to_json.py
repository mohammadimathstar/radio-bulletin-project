from schemas_promptfoo import BulletinExtraction
import json

with open("guardrail/entity_relation_promptfoo.json", "w") as f:
    json.dump(BulletinExtraction.model_json_schema(), f, indent=2)
