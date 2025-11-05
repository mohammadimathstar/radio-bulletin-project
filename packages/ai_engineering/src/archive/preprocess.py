### FILE: src/preprocess.py
"""
Utilities to convert text + entity offsets into BIO token labels.
This is intentionally simple: uses whitespace tokenization.
"""
from typing import List, Dict


def text_to_bio(text: str, entities: List[Dict]):
    # entities: list of dicts with start,end,type
    # tokenize by whitespace and return tokens and labels
    tokens = text.split()
    # build char->token index map
    offsets = []
    idx = 0
    for t in tokens:
        start = text.find(t, idx)
        end = start + len(t)
        offsets.append((start, end))
        idx = end

    labels = ['O'] * len(tokens)
    for ent in entities:
        s = ent['start']
        e = ent['end']
        ent_type = ent['type']
        # mark tokens that overlap
        for i, (ts, te) in enumerate(offsets):
            if te <= s or ts >= e:
                continue
            # overlap
            if labels[i] == 'O':
                labels[i] = 'B-' + ent_type
            else:
                labels[i] = 'I-' + ent_type

    return {'tokens': tokens, 'labels': labels}


