
import re


# Recognized legal judgment headings
PATTERNS = [
    r"^(?:JUDGMENT|ORDER|REPORTABLE|NON[- ]REPORTABLE)$",
    r"^(?:FACTS OF THE CASE|BRIEF FACTS|FACTUAL BACKGROUND)$",
    r"^(?:ISSUES?|QUESTIONS? FOR CONSIDERATION)$",
    r"^(?:SUBMISSIONS?|CONTENTIONS?)$",
    r"^(?:ANALYSIS|DISCUSSION|CONSIDERATION|REASONS)$",
    r"^(?:CONCLUSION|FINAL ORDER|OPERATIVE PART|DIRECTIONS)$",
]

# Compile normal headings
RX = [
    re.compile(p, re.IGNORECASE)
    for p in PATTERNS
]

# Roman numeral headings: uppercase only.
# Prevents lowercase "v." in case citations from matching.
ROMAN_PATTERN = re.compile(
    r"^(?:I|II|III|IV|V|VI|VII|VIII|IX|X)[.)]\s+[A-Z][A-Z\s,&()'-]{2,100}$"
)

# Numbered headings: require a short, heading-like line.
NUMBER_PATTERN = re.compile(
    r"^\d{1,3}[.)]\s+[A-Z][A-Za-z\s,&()'-]{2,90}$"
)


def is_valid_heading(line):

    s = re.sub(r"\s+", " ", line).strip()

    if not s:
        return False

    if len(s) > 130:
        return False

    # Ignore page markers
    if s.startswith("[PAGE"):
        return False

    # Ignore common case citation fragments
    if re.match(r"^v\.\s+", s):
        return False

    # Ignore sentences and long legal paragraphs
    if len(s.split()) > 15:
        return False

    # Check recognized legal headings
    if any(pattern.fullmatch(s) for pattern in RX):
        return True

    # Check uppercase Roman numeral headings
    if ROMAN_PATTERN.fullmatch(s):
        return True

    # Check numbered headings
    if NUMBER_PATTERN.fullmatch(s):
        return True

    return False


def build_toc(text, max_nodes=150):

    lines = text.splitlines()

    headings = []
    seen = set()

    for i, line in enumerate(lines):

        s = re.sub(r"\s+", " ", line).strip()

        if not is_valid_heading(s):
            continue

        key = s.lower()

        if key not in seen:

            seen.add(key)

            headings.append({
                "title": s,
                "line_index": i,
                "inferred": True
            })

    # Fallback when the judgment has very few recognizable headings
    if len(headings) < 3:

        step = max(40, len(lines) // 12)

        headings = []

        for i, start in enumerate(range(0, len(lines), step)):

            headings.append({
                "title": f"Inferred judgment segment {i + 1}",
                "line_index": start,
                "inferred": True
            })

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
                "end_line": end,
                "inferred": node.get("inferred", True)
            })

    return sections


def toc_text(toc):

    return "\n".join(
        "- " + item["title"]
        for item in toc
    )
