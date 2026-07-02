"""
CapsuleRecord dataclass and JSON serialization for the yplot2 catalog.

PURE module: only stdlib imports (dataclasses, json, collections.abc).
No matplotlib, seaborn, or pandas at module level or at all.
"""

import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class CapsuleRecord:
    """Static, render-free description of one @catalog capsule.

    All fields are populated from pure static introspection — no demo is ever
    executed during collection.
    """

    name: str
    category: str
    tags: tuple[str, ...]
    data_shape: str
    kind: str
    signature: str
    inputs: tuple[str, ...]
    summary: str
    source_path: str
    import_path: str
    has_demo: bool


def record_to_dict(rec: CapsuleRecord) -> dict[str, object]:
    """Serialize a CapsuleRecord to a plain dict for JSON output.

    Tuples are converted to lists so the result is JSON-serializable.

    Args:
        rec: The record to serialize.

    Returns:
        Dict with all fields; tuple fields become lists.
    """
    d = asdict(rec)
    d["tags"] = list(rec.tags)
    d["inputs"] = list(rec.inputs)
    return d


def catalog_to_json(records: Sequence[CapsuleRecord]) -> str:
    """Serialize records to deterministic pretty JSON.

    Output shape: ``{"schema_version": 1, "capsules": [...]}``.
    Records are sorted by ``(category, name)`` for stable output.
    Ends with a trailing newline.

    Args:
        records: CapsuleRecord instances to serialize.

    Returns:
        JSON string, indent=2, sorted by (category, name), trailing newline.
    """
    sorted_records = sorted(records, key=lambda r: (r.category, r.name))
    payload: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "capsules": [record_to_dict(r) for r in sorted_records],
    }
    return json.dumps(payload, indent=2) + "\n"
