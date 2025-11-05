"""
Run LLM inference to produce silver labels for a dataset.
Saves outputs to data/silver_labels/<run_name>.jsonl
"""
import json
import yaml
from tqdm import tqdm
import argparse
from pathlib import Path
from data_loader import read_dataframe, write_jsonl
from prompt_runner import PromptRunner

from packages.ai_engineering.src.guardrails_schemas.schemas_guard import BulletinExtraction  # updated schema with context_sentence & canonical_name

from dotenv import load_dotenv

load_dotenv()

def load_config(yaml_path):
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)

def main():

    # 1. CLI arguments
    parser = argparse.ArgumentParser(description="Run LLM inference")
    parser.add_argument("--config", default="./packages/ai_engineering/configs/settings.yaml", help="Path to YAML config")
    parser.add_argument("--model", help="Override: LLM model name")
    parser.add_argument("--batch_size", type=int, help="Override: batch size")
    parser.add_argument("--input", help="Override: input file (csv)")
    parser.add_argument("--out_dir", help="Override: output directory")
    parser.add_argument("--run_name", help="Override: run name")    
    parser.add_argument("--prompt_template", help="Override: prompt template")

    args = parser.parse_args()

    # 2. Load defaults from YAML
    cfg = load_config(args.config)

    # 3. Apply CLI overrides
    if args.model:
        cfg["model"] = args.model
    if args.batch_size:
        cfg["batch_size"] = args.batch_size
    if args.input:
        cfg["input"] = args.input
    if args.out_dir:
        cfg["out_dir"] = args.out_dir
    if args.run_name:
        cfg["run_name"] = args.run_name
    if args.prompt_template:
        cfg["prompt_template"] = args.prompt_template

    print(cfg["out_dir"])

    Path(cfg["out_dir"]).mkdir(parents=True, exist_ok=True)
    out_file = Path(cfg["out_dir"]) / f"{cfg["run_name"]}.jsonl"

    items = read_dataframe(cfg["input"] )

    runner = PromptRunner(cfg)

    # print(f"Starting the procedure (model: {cfg["model"]})")
    missing_doc = []
    results = []
    # Open output file once in append mode
    with open(out_file, "a", encoding="utf-8") as f_out:
        for i in tqdm(range(0, len(items), cfg["batch_size"])):
            # if i!=13: 
            #     continue
            batch = items[i : i + cfg["batch_size"]]
            
            ids = [x.get("id") or str(idx + i) for idx, x in enumerate(batch)]

            responses = runner.run_batch(batch, template_path=cfg["prompt_template"])
            if responses == 'null':
                print(f"Received 'null' response from the model for {ids}. Exiting.")
                responses = runner.run_batch(batch, template_path=cfg["prompt_template"])
                if responses == 'null':
                    print(f"Received 'null' response again from the model for {ids}. Skipping this batch.")
                    missing_doc.append(ids)
                    continue
            for doc_id, item, raw_out in zip(ids, batch, responses):
                text = item["text"]
                
                # Attempt to parse into our schema; keep raw and parsed
                try:
                    parsed = BulletinExtraction.model_validate(raw_out)    
                    
                    # parsed_json = parsed.dict()
                    parsed_json = parsed.model_dump(indent=2)
                    valid = True
                except Exception as e:
                    parsed_json = None
                    valid = False
                out = {
                    "id": doc_id,
                    "text": text,
                    "raw_output": raw_out,
                    "parsed": parsed_json,
                    "valid": valid,
                    "model": cfg["model"] ,
                }
                
                # --- NEW: write each record immediately ---
                f_out.write(json.dumps(out, ensure_ascii=False) + "\n")
                f_out.flush()  # ensure data is actually written to disk

                results.append(out)
        
    # write_jsonl([r for r in results], out_file)
    print(f"Wrote {len(results)} outputs to {out_file}")
    print(f"Missing docs for {len(missing_doc)} ids: {missing_doc}")

# python -m scripts.run_inference 
if __name__ == "__main__":
    main()

