"""
Metrics for NER and simple agreement scoring.
"""
from typing import List, Dict
from collections import defaultdict


def schema_validity_rate(preds: List[Dict]) -> float:
    total = 0
    valid = 0
    for p in preds:
        total += 1
        if p.get('valid'):
            valid += 1
    return valid / total if total else 0.0


def entities_to_spans(item):
    # returns list of (start, end, type)
    parsed = item.get('parsed')
    if not parsed:
        return []
    ents = parsed.get('entities', [])
    spans = []
    for e in ents:
        spans.append((e['start'], e['end'], e['type']))
    return spans


def compute_agreement_score(a: List[Dict], b: List[Dict]) -> float:
    # simple overlap-based agreement: (2 * intersection) / (len(a)+len(b)) averaged
    scores = []
    id_to_b = {x['id']: x for x in b}
    for x in a:
        y = id_to_b.get(x['id'])
        if not y:
            continue
        spans_a = set(entities_to_spans(x))
        spans_b = set(entities_to_spans(y))
        if not (spans_a or spans_b):
            scores.append(1.0)
            continue
        inter = len(spans_a & spans_b)
        denom = len(spans_a) + len(spans_b)
        score = (2 * inter / denom) if denom > 0 else 1.0
        scores.append(score)
    return sum(scores) / len(scores) if scores else 0.0


def compute_entity_level_f1(preds: List[Dict], gold: List[Dict]) -> float:
    # naive micro-F1 at span+type level
    id_to_gold = {x['id']: x for x in gold}
    tp = 0
    fp = 0
    fn = 0
    for p in preds:
        g = id_to_gold.get(p['id'])
        pred_spans = set(entities_to_spans(p))
        gold_spans = set(entities_to_spans(g)) if g else set()
        tp += len(pred_spans & gold_spans)
        fp += len(pred_spans - gold_spans)
        fn += len(gold_spans - pred_spans)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return f1


