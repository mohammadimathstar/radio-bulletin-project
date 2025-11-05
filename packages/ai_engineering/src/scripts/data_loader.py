"""
Simple jsonl reader/writer utilities.
"""
import json
from pathlib import Path
import pandas as pd
from typing import List, Dict

def read_dataframe(path) -> List[Dict]:
    """
    Convert a DataFrame to a list of dicts for inference.

    Each row in the DataFrame should have columns:
        - 'date' : date of the bulletin
        - 'recordIdentifier' : unique ID
        - 'content' : text of the bulletin

    Returns a list of dicts:
    [
        {"id": ..., "text": ..., "json_input": {"date": ..., "language": ...}},
        ...
    ]
    """
    df = pd.read_csv(path)
    
    items = []
    for _, row in df.iterrows():
        items.append({
            "id": row["recordIdentifier"],
            "text": row["content"],
            "json_input": {
                "date": row["date"],
                "language": "Dutch"  # assuming language is always Dutch
            }
        })
    return items


def read_jsonl(path):
    path = Path(path)
    items = []
    with path.open('r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def write_jsonl(items, path_or_file):
    """
    Write a list of Python dictionaries to a JSONL (JSON Lines) file.

    Each dictionary in `items` will be serialized as a single JSON object
    on its own line in the output file.

    Parameters
    ----------
    items : list of dict
        The data to write. Each element should be a Python dictionary that
        can be serialized to JSON.
    path_or_file : str or pathlib.Path
        Path to the output file or directory. If a directory is provided or
        the path does not end with '.jsonl', the function will create a
        default file named 'out.jsonl' inside that directory.

    Example
    -------
    >>> data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    >>> write_jsonl(data, "output.jsonl")
    This will create 'output.jsonl' with two lines, each a JSON object.
    """

    path = Path(path_or_file)
    if not str(path).endswith('.jsonl'):
        path = Path(path) / 'out.jsonl'
    with path.open('w', encoding='utf8') as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + '\n')



