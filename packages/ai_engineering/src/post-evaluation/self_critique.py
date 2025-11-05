### FILE: scripts/self_critique.py
"""
Ask the LLM to critique its own extraction. This script appends a self_critique field to each prediction.
"""
import argparse
import json
from pathlib import Path
from scripts.run_inference import load_config
from src.data_loader import read_jsonl, write_jsonl
from src.prompt_runner import PromptRunner

from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/settings_self_critique.yaml", help="Path to YAML config")
    parser.add_argument('--preds', help='predictions jsonl')
    parser.add_argument('--model', help='LLM model name (overrides config)')
    parser.add_argument('--prompt_template', help='Path to the prompt template file (overrides config)')
    args = parser.parse_args()

    cfg = load_config(args.config)

    if args.model:
        cfg["model"] = args.model
    if args.prompt_template:
        cfg["prompt_template"] = args.prompt_template
    if args.preds:
        cfg["preds"] = args.preds
   

    preds = read_jsonl(cfg["preds"])
    runner = PromptRunner(cfg)

    print(cfg['preds'])
    out_path = cfg['preds'].replace('.jsonl', '.selfcritique.jsonl')
    results = []
    with open(out_path, "a", encoding="utf-8") as f_out:
        for p in preds:
            text = p['text']
            # parsed = p.get('parsed') or {}
            parsed = json.dumps('raw_output') or {}

            # build input: include raw extracted JSON and ask for critique
            instruction = {
                'text': text,
                'extracted': json.loads(parsed)  # or parsed.dict() if using older Pydantic
            }
            
            resp = runner.run(text=instruction['text'], json_input=instruction, template_path=cfg["prompt_template"])

            # run(self, text: str = None, json_input: dict = None, template_path: str = None)
            p['self_critique'] = resp

            f_out.write(json.dumps(p, ensure_ascii=False) + "\n")
            f_out.flush()  # ensure data is actually written to disk
            results.append(p)

    print(f'Wrote self-critique outputs to {out_path}')


# python -m scripts.self_critique  --preds <path_to_preds.jsonl>
if __name__ == "__main__":
    main()