#!/usr/bin/env python3
"""audit_remove.py -- find CoCalc `remove` metadata before running nbgrader update.

`remove` is a CoCalc extension to the nbgrader cell schema; upstream nbgrader
has no such key and its Create Assignment toolbar never writes one.  Because
the v3 schema sets additionalProperties=false, any cell carrying it fails
CheckCellMetadata and kills generate_assignment.

`nbgrader update` fixes the validation error by DELETING the key.  For cells
with `remove: false` that is harmless.  For cells with `remove: true` it
silently changes behaviour: CoCalc was stripping those cells from the student
version, and after the update they will be released to students.

Run this first, decide what to do with each `remove: true` cell, and only
then run `nbgrader update`.

    python3 audit_remove.py /path/to/course/source
"""

import json
import os
import sys


def audit(root):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if not d.startswith(".") and d != ".ipynb_checkpoints"]
        for fn in sorted(filenames):
            if not fn.endswith(".ipynb"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, encoding="utf-8") as fh:
                    nb = json.load(fh)
            except (OSError, ValueError) as exc:
                print(f"!! could not read {path}: {exc}")
                continue
            for i, cell in enumerate(nb.get("cells", [])):
                meta = cell.get("metadata", {}).get("nbgrader", {})
                if "remove" not in meta:
                    continue
                source = "".join(cell.get("source", []))
                hits.append({
                    "path": path,
                    "index": i,
                    "grade_id": meta.get("grade_id", "<none>"),
                    "cell_type": cell.get("cell_type"),
                    "remove": meta["remove"],
                    "preview": source[:90].replace("\n", " | "),
                })
    return hits


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    hits = audit(root)

    dangerous = [h for h in hits if h["remove"]]
    benign = [h for h in hits if not h["remove"]]

    print(f"Scanned {root}")
    print(f"  cells with remove: false -> {len(benign):3d}  "
          f"(safe; nbgrader update just deletes the key)")
    print(f"  cells with remove: true  -> {len(dangerous):3d}  "
          f"(REVIEW THESE -- they will become visible to students)")
    print()

    for h in dangerous:
        print(f"  {h['path']}  cell {h['index']}  "
              f"[{h['grade_id']}]  ({h['cell_type']})")
        print(f"      {h['preview']}")
    if dangerous:
        print()
        print("For each of the above, pick one:")
        print("  (a) delete the cell from source/ entirely")
        print("  (b) move the content into a comment in an adjacent cell")
        print("  (c) tag it 'instructor-only' and add TagRemovePreprocessor")
        print("      to c.GenerateAssignment.preprocessors")
    return 1 if dangerous else 0


if __name__ == "__main__":
    sys.exit(main())
