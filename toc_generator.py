import re
PATS=[r"^(?:JUDGMENT|ORDER|REPORTABLE|NON[- ]REPORTABLE)$",
r"^(?:FACTS OF THE CASE|BRIEF FACTS|FACTUAL BACKGROUND)$",
r"^(?:ISSUES? FOR (?:CONSIDERATION|DETERMINATION).*)$",
r"^(?:SUBMISSIONS? ON BEHALF OF.*|CONTENTIONS? OF.*)$",
r"^(?:ANALYSIS|DISCUSSION|CONSIDERATION|REASONS)$",
r"^(?:CONCLUSION|FINAL ORDER|OPERATIVE PART|DIRECTIONS)$",
r"^(?:[IVX]+[.)]\\s+[A-Z][A-Z ,&()'-]{3,100})$",
r"^(?:[0-9]{1,3}[.)]\\s+[A-Z][A-Za-z ,&()'-]{3,100})$"]
RX=[re.compile(x,re.I) for x in PATS]
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
