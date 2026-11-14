import os,json,requests
from dotenv import load_dotenv
load_dotenv()
KEY=os.getenv("OPENROUTER_API_KEY"); MODEL=os.getenv("OPENROUTER_MODEL","openai/gpt-4o-mini")
def qa(title,body):
    prompt=("Create 2 factual questions answerable ONLY from this Indian Supreme Court judgment section. "
    "Return JSON array with question, answer, gold_leaf. gold_leaf must exactly equal section title. "
    "Do not invent case facts or legal citations.\nSECTION: "+title+"\nTEXT:\n"+body[:8000])
    r=requests.post("https://openrouter.ai/api/v1/chat/completions",
      headers={"Authorization":"Bearer "+KEY,"Content-Type":"application/json"},
      json={"model":MODEL,"temperature":0.1,"messages":[{"role":"user","content":prompt}]},timeout=120)
    r.raise_for_status(); s=r.json()["choices"][0]["message"]["content"].strip()
    return json.loads(s.removeprefix("```json").removesuffix("```").strip())
count=0
with open("data/structured_judgments.jsonl",encoding="utf8") as f,open("data/stair_train.jsonl","w",encoding="utf8") as o:
    for line in f:
        d=json.loads(line)
        for sec in d["sections"]:
            try: items=qa(sec["title"],sec["text"])
            except Exception as e: print("QA skip:",e); continue
            for x in items:
                x.update({"doc_id":d["doc_id"],"toc":[n["title"] for n in d["toc"]]})
                o.write(json.dumps(x,ensure_ascii=False)+"\n"); count+=1
                if count>=500: break
            if count>=500: break
        if count>=500: break
print("Training examples:",count)
