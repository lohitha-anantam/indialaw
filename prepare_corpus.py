import json
from pathlib import Path
from document_parser import iter_documents
from toc_generator import build_toc,attach_sections
Path("data").mkdir(exist_ok=True)
with open("data/structured_judgments.jsonl","w",encoding="utf8") as f:
    count=0
    for d in iter_documents("data/kaggle"):
        toc=build_toc(d["text"]); secs=attach_sections(d["text"],toc)
        if secs:
            f.write(json.dumps({**d,"toc":toc,"sections":secs},ensure_ascii=False)+"\n"); count+=1
print("Prepared judgments:",count)
