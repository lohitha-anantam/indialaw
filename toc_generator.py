
import re

PATTERNS = [
    r"^(?:JUDGMENT|ORDER|REPORTABLE|NON[- ]REPORTABLE)$",
    r"^(?:FACTS OF THE CASE|BRIEF FACTS|FACTUAL BACKGROUND)$",
    r"^(?:ISSUES?|QUESTIONS? FOR CONSIDERATION).*",
    r"^(?:SUBMISSIONS?|CONTENTIONS?).*",
    r"^(?:ANALYSIS|DISCUSSION|CONSIDERATION|REASONS)$",
    r"^(?:CONCLUSION|FINAL ORDER|OPERATIVE PART|DIRECTIONS)$",
    r"^(?:[IVX]+[.)]\s+.+)$",
    r"^(?:\d{1,3}[.)]\s+[A-Z].+)$"
]

RX = [re.compile(p, re.IGNORECASE) for p in PATTERNS]


def build_toc(text, max_nodes=150):

    lines = text.splitlines()
    headings = []
    seen = set()

    for i, line in enumerate(lines):

        s = re.sub(r"\s+", " ", line).strip()

        if not s or len(s) > 130:
            continue

        if s.startswith("[PAGE"):
            continue

        if any(r.match(s) for r in RX):

            key = s.lower()

            if key not in seen:
                seen.add(key)

                headings.append({
                    "title": s,
                    "line_index": i,
                    "inferred": True
                })

    # Fallback for judgments with few recognizable headings
    if len(headings) < 3:

        step = max(40, len(lines) // 12)

        headings = [
            {
                "title": f"Inferred judgment segment {i + 1}",
                "line_index": i,
                "inferred": True
            }
            for i in range(0, len(lines), step)
        ]

    return headings[:max_nodes]


def attach_sections(text, toc):

    lines = text.splitlines()
    sections = []

    for i, node in enumerate(toc):

        start = node["line_index"]

        end = (
            toc[i + 1]["line_index"]
            if i + 1 < len(toc)
            else len(lines)
        )

        body = "\n".join(lines[start:end]).strip()

        if len(body) > 150:

            sections.append({
                "title": node["title"],
                "text": body,
                "start_line": start,
                "end_line": end
            })

    return sections


def toc_text(toc):
    return "\n".join(
        "- " + item["title"]
        for item in toc
    )
