"""Flatten a LaTeX main file (recursive \\input), number floats in document order,
and list every \\ref/\\autoref site with its resolved float number.

Usage: python -X utf8 float_ref_map2.py <tex_root> <main.tex>
Read-only. Deterministic. JSON to stdout.

Line/char positions are anchored to the ORIGINAL file that physically contains the
text, so a locator produced here is (file, line) and never ambiguous.
"""
import json
import re
import sys
from pathlib import Path

FLOAT_ENVS = ("table*", "table", "figure*", "figure")
REF_MACRO = re.compile(r"\\(autoref|ref)\{([^}]*)\}")
INPUT_MACRO = re.compile(r"\\input\{([^}]*)\}")


def strip_comments(text: str) -> str:
    out = []
    for ln in text.split("\n"):
        m = re.search(r"(?<!\\)%", ln)
        out.append(ln[: m.start()] if m else ln)
    return "\n".join(out)


def resolve_input(ref: str, cur: Path, root: Path):
    cands = [ref, ref + ".tex"]
    for c in cands:
        for base in (cur.parent, root):
            p = (base / c)
            if p.is_file():
                return p
    return None


def flatten(main: Path, root: Path, limit: int = 64):
    """Return list of chunks: dict(file, first_line, text) in DOCUMENT order."""
    chunks = []
    seen = set()

    def walk(f: Path):
        if f in seen or len(seen) > limit:
            return
        seen.add(f)
        src = strip_comments(f.read_text(encoding="utf-8", errors="replace"))
        pos = 0
        line = 1  # 1-based line of src at pos
        for m in INPUT_MACRO.finditer(src):
            if m.start() > pos:
                chunks.append({"file": str(f.relative_to(root)).replace("\\", "/"),
                               "start_line": line,
                               "text": src[pos : m.start()],
                               "offset_in_src": pos})
                line += src[pos : m.start()].count("\n")
            t = resolve_input(m.group(1).strip(), f, root)
            if t is None:
                chunks.append({"file": str(f.relative_to(root)).replace("\\", "/"),
                               "start_line": line,
                               "text": "[UNRESOLVED_INPUT:%s]" % m.group(1),
                               "offset_in_src": m.start(), "unresolved": m.group(1)})
                pos = m.end()
            else:
                walk(t)
                pos = m.end()
        if pos < len(src):
            chunks.append({"file": str(f.relative_to(root)).replace("\\", "/"),
                           "start_line": line, "text": src[pos:], "offset_in_src": pos})

    walk(main)
    return chunks


def abs_line(chunk: dict, rel_pos: int):
    base = chunk["start_line"] - 1 + chunk["text"][:rel_pos].count("\n")
    return base + 1


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    main_tex = Path(sys.argv[2]).resolve()
    chunks = flatten(main_tex, root)

    doc = "".join(c["text"] for c in chunks)

    # locate each chunk's start offset in doc for char->chunk mapping
    starts, acc = [], 0
    for c in chunks:
        starts.append(acc)
        acc += len(c["text"])

    def chunk_at(gpos: int):
        lo, hi = 0, len(chunks) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if starts[mid] <= gpos:
                lo = mid
            else:
                hi = mid - 1
        return chunks[lo], gpos - starts[lo]

    # 1) floats in document order
    envs = sorted(FLOAT_ENVS, key=len, reverse=True)
    begins = []
    for m in re.finditer(r"\\begin\{(table\*|table|figure\*|figure)\}", doc):
        begins.append(m)
    # naive nesting: env bodies must not nest for these papers; verify with depth counter
    depth = 0
    max_depth = 0
    for m in re.finditer(r"\\begin\{(?:table\*|table|figure\*|figure)\}|\\end\{(?:table\*|table|figure\*|figure)\}", doc):
        if m.group(0).startswith("\\begin"):
            depth += 1
            max_depth = max(max_depth, depth)
        else:
            depth -= 1
    floats = []
    tnum = fnum = 0
    label_index = {}
    for m in begins:
        env = m.group(1)
        # matching \end{env}
        e = re.search(r"\\end\{" + re.escape(env) + r"\}", doc[m.end():])
        inner = doc[m.end() : m.end() + (e.start() if e else len(doc))]
        labs = re.findall(r"\\label\{([^}]*)\}", inner)
        cap = re.search(r"\\caption\s*(?:\[[^\]]*\])?\{", inner)
        if env.startswith("table"):
            tnum += 1
            kind, num = "table", tnum
        else:
            fnum += 1
            kind, num = "figure", fnum
        ch, rp = chunk_at(m.start())
        floats.append({
            "env": env, "kind": kind, "number": num,
            "file": ch["file"], "line": abs_line(ch, rp),
            "labels": labs, "caption_present": bool(cap),
        })
        for l in labs:
            label_index[l] = {"kind": kind, "number": num, "file": ch["file"], "line": abs_line(ch, rp)}

    # 2) all ref sites across the flattened document
    sites = []
    for m in REF_MACRO.finditer(doc):
        ch, rp = chunk_at(m.start())
        macro, key = m.group(1), m.group(2)
        pre = re.sub(r"\s+", " ", doc[max(0, m.start() - 120) : m.start()])[-100:]
        sites.append({
            "macro": "\\" + macro, "target": key,
            "file": ch["file"], "line": abs_line(ch, rp),
            "resolved": label_index.get(key, {"kind": "UNRESOLVED"}),
            "preceding": pre,
        })

    unresolved_refs = [s for s in sites if s["resolved"]["kind"] == "UNRESOLVED"]
    dangling_labels = sorted(set(label_index) - {s["target"] for s in sites})

    out = {
        "chunk_order": [{"file": c["file"], "start_line": c["number"] if False else c["start_line"],
                         "chars": len(c["text"])} for c in chunks],
        "max_float_nesting": max_depth,
        "tables": [f for f in floats if f["kind"] == "table"],
        "figures": [f for f in floats if f["kind"] == "figure"],
        "ref_sites": sites,
        "unresolved_refs": unresolved_refs,
        "never_referenced_labels": dangling_labels,
    }
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
