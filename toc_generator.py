
import re

def build_toc(text, max_nodes=150):

    lines = text.splitlines()
    headings = []

    patterns = [
        r"^(FACTS|BACKGROUND|INTRODUCTION)",
        r"^(ISSUES?|QUESTIONS? FOR CONSIDERATION)",
        r"^(SUBMISSIONS?|CONTENTIONS?)",
        r"^(ANALYSIS|DISCUSSION|REASONS)",
        r"^(LEGAL POSITION|APPLICABLE LAW)",
        r"^(CONCLUSION|FINAL ORDER|DIRECTIONS)",
        r"^([IVX]+[\.\)]\s+.+)",
        r"^(\d{1,3}[\.\)]\s+[A-Z].+)",
        r"^(JUDGMENT|ORDER|HELD)",
    ]

    for i, line in enumerate(lines):

        line = re.sub(r"\s+", " ", line).strip()

        if not line or len(line) > 150:
            continue

        # Ignore page markers
        if line.startswith("[PAGE"):
            continue

        for pattern in patterns:
            if re.match(pattern, line, re.IGNORECASE):
                headings.append({
                    "title": line,
                    "line_index": i,
                    "inferred": True
                })
                break

    # Remove duplicate headings
    unique = []
    seen = set()

    for item in headings:
        key = item["title"].lower()

        if key not in seen:
            seen.add(key)
            unique.append(item)

    # Fallback: divide long judgments into smaller segments
    if len(unique) < 3:

        step = max(40, len(lines) // 12)

        unique = [
            {
                "title": f"Inferred judgment segment {i+1}",
                "line_index": i,
                "inferred": True
            }
            for i in range(0, len(lines), step)
        ]

    return unique[:max_nodes]

def build_toc(text):
    lines=text.splitlines(); out=[]; seen=set()
    for i,line in enumerate(lines):
        s=" ".join(line.split()).strip(" :-")
        if s and len(s)<130 and any(r.match(s) for r in RX) and s.lower() not in seen:
            seen.add(s.lower()); out.append({"title":s,"line_index":i,"inferred":True})
    if not out:
        step=max(100,len(lines)//8 or 100)
        out=[{"title":f"Inferred judgment segment {i+1}","line_index":i,"inferred":True} for i in range(0,len(lines),step)]
    return out[:120]
def attach_sections(text,toc):
    lines=text.splitlines(); out=[]
    for i,n in enumerate(toc):
        a=n["line_index"]; b=toc[i+1]["line_index"] if i+1<len(toc) else len(lines)
        body="\n".join(lines[a:b]).strip()
        if len(body)>150: out.append({"title":n["title"],"text":body,"start_line":a,"end_line":b})
    return out
def toc_text(toc): return "\n".join("- "+x["title"] for x in toc)
