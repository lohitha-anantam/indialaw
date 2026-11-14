import os,streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from document_parser import read_document
from toc_generator import build_toc,toc_text
from stair_core import predict_section,retrieve,answer
load_dotenv()
st.set_page_config(page_title="Supreme Court STAIR",page_icon="⚖️",layout="wide")
st.title("⚖️ Indian Supreme Court Judgment – STAIR Assistant")
st.caption("Upload a judgment, predict its relevant section, retrieve evidence and generate a grounded answer.")
for k in ["OPENROUTER_API_KEY","OPENROUTER_MODEL","KAGGLE_API_TOKEN","KAGGLE_DATASET","STAIR_ADAPTER_PATH"]:
    if k in st.secrets: os.environ[k]=str(st.secrets[k])
f=st.file_uploader("Upload Supreme Court judgment",type=["pdf","txt","md","html","htm","docx"])
if f:
    p=Path("data")/f.name; p.parent.mkdir(exist_ok=True); p.write_bytes(f.getvalue())
    text=read_document(p)
    if len(text)<500: st.error("Could not extract enough text. Scanned PDFs need OCR."); st.stop()
    toc=build_toc(text)
    st.success(f"Extracted {len(text):,} characters; found {len(toc)} candidate headings.")
    st.warning("Headings are inferred automatically and may not be official court headings. Verify them against the judgment.")
    with st.expander("View extracted structure"): st.code(toc_text(toc))
    q=st.text_area("Ask a question about this judgment")
    if st.button("Retrieve evidence and answer",type="primary",disabled=not q.strip()):
        with st.spinner("Retrieving..."):
            section,mode=predict_section(q,toc,os.getenv("STAIR_ADAPTER_PATH","artifacts/supreme-court-stair"))
            ev=retrieve(q,text,toc)
        st.subheader("Predicted section"); st.write(section); st.caption("Retriever mode: "+mode)
        if mode=="embedding_baseline": st.warning("No trained adapter loaded. This is a baseline, not trained STAIR.")
        st.subheader("Answer")
        try: st.write(answer(q,ev))
        except Exception as e: st.error(str(e))
        st.subheader("Evidence")
        for i,x in enumerate(ev,1):
            with st.expander(f"{i}. {x['title']} | score {x['score']:.3f}"): st.write(x["text"][:10000])
else: st.info("Upload a new judgment PDF to test. Training is prepared separately.")
