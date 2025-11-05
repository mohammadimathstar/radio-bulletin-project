
### FILE: scripts/evaluate_outputs.py
"""
Evaluate model outputs against a gold or silver eval set.
If no gold available, this will compute inter-model agreement or schema validity.
"""
import argparse
from pathlib import Path
from src.data_loader import read_jsonl
from src.metrics import compute_entity_level_f1, compute_agreement_score, schema_validity_rate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred", required=True, help="predictions jsonl (from run_inference)")
    parser.add_argument("--gold", required=False, help="gold jsonl with parsed labels to compare to")
    parser.add_argument("--other", required=False, help="another predictions file for agreement")
    args = parser.parse_args()
    
    # Init W&B
    wandb.init(project="ner-re-extraction", name="eval_run")

    preds = read_jsonl(args.pred)

    print(f"Loaded {len(preds)} predictions")

    validity = schema_validity_rate(preds)
    print(f"Schema validity rate: {validity:.3f}")
    
    wandb.log({"schema_validity": validity})
    
    # If gold eval set exists
    if args.gold:
        gold = read_jsonl(args.gold)
        f1 = compute_entity_level_f1(preds, gold)
        print(f"Entity-level F1 vs gold: {f1:.3f}")
        wandb.log({"entity_f1": f1})
    
    # Inter-model agreement
    if args.other:
        other = read_jsonl(args.other)
        agreement = compute_agreement_score(preds, other)
        print(f"Inter-model agreement: {agreement:.3f}")
        wandb.log({"agreement": agreement})


if __name__ == '__main__':
    main()


