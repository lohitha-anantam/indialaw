import os,re
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from toc_generator import attach_sections,toc_text
def embedder(): return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
def predict_section(question,toc,adapter="artifacts/supreme-court-stair"):
    if Path(adapter).exists():
        try:
            import torch
            from transformers import AutoTokenizer,AutoModelForCausalLM
            from peft import PeftModel
            base="mistralai/Mistral-7B-Instruct-v0.2"
            tok=AutoTokenizer.from_pretrained(adapter)
            model=AutoModelForCausalLM.from_pretrained(base,device_map="auto",torch_dtype=torch.float16,load_in_4bit=True)
            model=PeftModel.from_pretrained(model,adapter)
            p="Choose one exact ToC section. Return only its title.\n"+toc_text(toc)+"\nQUESTION: "+question+"\nSECTION:"
            x=tok(p,return_tensors="pt",truncation=True,max_length=4096).to(model.device)
            y=model.generate(**x,max_new_tokens=64,do_sample=False)
            ans=tok.decode(y[0][x["input_ids"].shape[1]:],skip_special_tokens=True)
            for n in toc:
                if n["title"].lower() in ans.lower(): return n["title"],"trained_stair"
        except Exception as e: print("Adapter error",e)
    em=embedder(); names=[n["title"] for n in toc]
    if not names:return None,"no_sections"
    q=em.encode([question],normalize_embeddings=True); v=em.encode(names,normalize_embeddings=True)
    return names[int(np.argmax(v@q[0]))],"embedding_baseline"
def retrieve(question,text,toc,k=5):
    secs=attach_sections(text,toc); parts=re.split(r"\\[PAGE\\s+(\\d+)\\]",text)
    for i in range(1,len(parts),2):
        if parts[i+1].strip(): secs.append({"title":"PDF Page "+parts[i],"text":parts[i+1],"page":parts[i]})
    if not secs:return []
    em=embedder(); q=em.encode([question],normalize_embeddings=True)
    v=em.encode([s["title"]+"\\n"+s["text"][:6000] for s in secs],normalize_embeddings=True)
    ids=np.argsort(v@q[0])[::-1][:k]
    return [{**secs[i],"score":float((v@q[0])[i])} for i in ids]
def answer(question,evidence):
    import requests
    key=os.getenv("OPENROUTER_API_KEY","")
    if not key:return "Set OPENROUTER_API_KEY in Streamlit Secrets."
    ctx="\\n\\n".join("SOURCE: "+x["title"]+"\\n"+x["text"][:5000] for x in evidence)
    prompt=("Answer only from supplied judgment evidence. Do not invent facts, legal provisions, "
    "holdings or citations. Distinguish court findings from party submissions. If evidence is "
    "insufficient, say so. This is legal information, not legal advice. Cite source labels.\\n\\n"
    +ctx+"\\n\\nQUESTION: "+question)
    r=requests.post("https://openrouter.ai/api/v1/chat/completions",
      headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},
      json={"model":os.getenv("OPENROUTER_MODEL","openai/gpt-4o-mini"),"temperature":0.1,"messages":[{"role":"user","content":prompt}]},timeout=120)
    r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]
