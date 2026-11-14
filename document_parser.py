from pathlib import Path
import re, fitz
from bs4 import BeautifulSoup
from docx import Document
EXTS={".pdf",".txt",".md",".html",".htm",".docx"}
def read_document(path):
    p=Path(path); ext=p.suffix.lower()
    if ext==".pdf":
        d=fitz.open(p); s="\n".join(f"[PAGE {i+1}]\n{x.get_text('text')}" for i,x in enumerate(d))
    elif ext in {".txt",".md"}: s=p.read_text(errors="ignore")
    elif ext in {".html",".htm"}: s=BeautifulSoup(p.read_text(errors="ignore"),"html.parser").get_text("\n")
    elif ext==".docx": s="\n".join(x.text for x in Document(p).paragraphs)
    else: return ""
    return re.sub(r"\n{3,}","\n\n",s).strip()
def iter_documents(root):
    for p in Path(root).rglob("*"):
        if p.is_file() and p.suffix.lower() in EXTS:
            try:
                t=read_document(p)
                if len(t)>500: yield {"doc_id":p.stem,"source":str(p),"text":t}
            except Exception as e: print("Skip",p,e)
