"""Enumerate LaTeX floats in source order and map label -> float number, ref -> site.

Usage: python -X utf8 float_ref_map.py <tex_root_dir> <main.tex>
Read-only. Prints JSON to stdout.
"""
import json
import re
import sys
from pathlib import Path

FLOAT_ENVS = ("table", "table*", "figure", "figure*")


def tex_files(root: Path):
    out = {}
    for p in sorted(root.rglob("*.tex")):
        out[p.name] = p
    return out


def strip_comments(text: str) -> str:
    lines = []
    for ln in text.split("\n"):
        m = re.search(r"(?<!\\)%", ln)
        lines.append(ln[: m.start()] if m else ln)
    return "\n".join(lines)


def main() -> int:
    root = Path(sys.argv[1])
    main_tex = Path(sys.argv[2])
    files = tex_files(root)

    main_src = strip_comments(main_tex.read_text(encoding="utf-8", errors="replace"))

    # Which local files does main.tex \input, and in what order?
    inputs = [m.group(1) for m in re.finditer(r"\\input\{([^}]*)\}", main_src)]

    # Build the concatenated source in document order: inline main + inputs at their
    # \input sites. Float numbering in LaTeX follows the *auxiliary* order, i.e. the
    # order floats appear in the final document, which equals \input order.
    seq = []
    pos = 0
    ann = []
    for m in re.finditer(r"\\input\{([^}]*)\}", main_src):
        name = m.group(1)
        cand = [n for n in files if n == name or n == name + ".tex"]
        seq.append(("main", main_src[pos : m.start()]))
        ann.append((len(seq) - 1, name, bool(cand)))
        if cand:
            seq.append(("input:" + cand[0], strip_comments(files[cand[0]].read_text("utf-8", errors="replace"))))
        pos = m.end()
    seq.append(("main", main_src[pos:]))

    # Walk the sequence, tracking line numbers per chunk for locators.
    floats = []
    labels = {}
    chunk_of_label = {}
    for idx, (src_name, body) in enumerate(seq):
        # find env begins
        for m in re.finditer(r"\\begin\{(" + "|".join(re.escape(e) for e in FLOAT_ENVS) + r")\}", body):
            env = m.group(1)
            # section-ish context: nearest preceding \section/\subsection in main chunks
            # number floats per type in document order
            endm = re.search(r"\\end\{" + re.escape(env).replace(r"\*", r"\*") + r"\}", body[m.end():])
            inner = body[m.end() : m.end() + (endm.start() if endm else len(body))]
            lab = re.findall(r"\\label\{([^}]*)\}", inner)
            cap = re.search(r"\\caption\{(.*?)\}\s*(?:\\label)?", inner, re.S)
            floats.append(
                {
                    "env": env,
                    "source": src_name,
                    "line": body[: m.start()].count("\n") + 1,
                    "labels": lab,
                    "has_caption": bool(cap),
                }
            )
            for l in lab:
                labels[l] = len([f for f in floats if f["env"].startswith("table") == env.startswith("table")])
                # recompute properly below
                chunk_of_label[l] = src_name
        # also collect labels outside floats (sections, equations) -- only tables matter here

    # Recompute table/figure numbering cleanly in document order.
    tcount = 0
    fcount = 0
    for fl in floats:
        if fl["env"].startswith("table"):
            tcount += 1
            fl["number"] = tcount
        else:
            fcount += 1
            fl["number"] = fcount
        for l in fl["labels"]:
            if fl["env"].startswith("table"):
                labels[l] = ("table", fl["number"])
            else:
                labels[l] = ("figure", fl["number"])

    # All \ref / \autoref sites in main.tex, with target resolution.
    sites = []
    for m in re.finditer(r"\\(?:auto)?ref\{([^}]*)\}", main_src):
        key = m.group(1)
        line = main_src[: m.start()].count("\n") + 1
        pre = main_src[max(0, m.start() - 90) : m.start()]
        sites.append(
            {
                "line": line,
                "macro": m.group(0),
                "target": key,
                "resolved": labels.get(key, "UNRESOLVED"),
                "preceding": re.sub(r"\s+", " ", pre)[-80:],
            }
        )

    print(
        json.dumps(
            {
                "input_order": ann,
                "floats": floats,
                "label_to_float": labels,
                "ref_sites": sites,
            },
            indent=1,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
