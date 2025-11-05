### FILE: scripts/compare_models.py
"""
Compare two model output files and compute agreement breakdowns.
"""
import argparse
from src.data_loader import read_jsonl
from src.metrics import compute_agreement_score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--a', required=True)
    parser.add_argument('--b', required=True)
    args = parser.parse_args()

    a = read_jsonl(args.a)
    b = read_jsonl(args.b)
    score = compute_agreement_score(a, b)
    print(f'Agreement between {args.a} and {args.b}: {score:.4f}')


if __name__ == '__main__':
    main()


