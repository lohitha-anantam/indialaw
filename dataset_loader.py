import os, shutil, kagglehub
from pathlib import Path
def download_dataset(slug="vangap/indian-supreme-court-judgments", out="data/kaggle"):
    if os.getenv("KAGGLE_API_TOKEN"):
        os.environ["KAGGLE_API_TOKEN"] = os.getenv("KAGGLE_API_TOKEN")
    src=Path(kagglehub.dataset_download(slug)); dst=Path(out); dst.mkdir(parents=True,exist_ok=True)
    if not any(dst.iterdir()):
        for p in src.iterdir():
            if p.is_dir(): shutil.copytree(p,dst/p.name,dirs_exist_ok=True)
            else: shutil.copy2(p,dst/p.name)
    return str(dst)
if __name__=="__main__":
    import sys
    print(download_dataset(sys.argv[1] if len(sys.argv)>1 else "vangap/indian-supreme-court-judgments"))
