"""Extract every Table/Figure reference sentence with the float it resolves to.

Usage: python -X utf8 ref_sentences.py <tex> <label> <label> ...
Read-only; prints one JSON object per reference site.
"""
import json
import re
import sys
from pathlib import Path

tex = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
lines = tex.split("\n")
want = sys.argv[2:]

# label -> (kind, number) by document order
counter = {"table": 0, "figure": 0}
lab_index = {}
for m in re.finditer(r"\\begin\{(table\*|table|figure\*|figure)\}", tex):
    kind = "table" if m.group(1).startswith("table") else "figure"
    counter[kind] += 1
    end = re.search(r"\\end\{" + re.escape(m.group(1)) + r"\}", tex[m.end():])
    inner = tex[m.end() : m.end() + (end.start() if end else 0)]
    for l in re.findall(r"\\label\{([^}]*)\}", inner):
        lab_index[l] = (kind, counter[kind])

pat = re.compile(r"((?:Table|Figure|Tab\.|Fig\.)?[^.]*?\\(?:auto)?ref\{([^}]*)\}[^.]*?\.)")
out = []
for i, ln in enumerate(lines, start=1):
    for m in re.finditer(r"\\(?:auto)?ref\{([^}]*)\}", ln):
        lab = m.group(1)
        if lab not in lab_index and not want:
            continue
        if want and lab not in want:
            continue
        sent_start = max(0, m.start() - 160)
        out.append(
            {
                "line": i,
                "label": lab,
                "resolves_to": lab_index.get(lab, "UNRESOLVED"),
                "context": re.sub(r"\s+", " ", ln[sent_start : m.end() + 200]),
            }
        )
print(json.dumps(out, indent=1, ensure_ascii=False))
