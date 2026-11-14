# Indian Supreme Court STAIR

Kaggle dataset default: `vangap/indian-supreme-court-judgments`.

## Pipeline
Kaggle judgments -> text/page extraction -> inferred structure/ToC -> synthetic QA -> LoRA training (query + complete ToC -> exact gold leaf) -> constrained candidate section selection -> evidence retrieval -> OpenRouter grounded answer.

**Caution:** Indian judgments do not consistently have formal ToCs. `toc_generator.py` infers candidate headings; they are not official court headings. Manually inspect the ToC and synthetic labels. Scanned PDFs need OCR; OCR is not included.

## Setup
```bash
pip install -r requirements.txt
copy .env.example .env
```
Fill `.env` with Kaggle token, OpenRouter key and dataset slug. Never commit secrets.

## Prepare corpus
```bash
python dataset_loader.py vangap/indian-supreme-court-judgments
python prepare_corpus.py
python generate_training_data.py
```
Inspect `data/structured_judgments.jsonl` and `data/stair_train.jsonl` before training. Split evaluation by judgment/case to avoid leakage.

## Train (GPU required; use Colab, not Streamlit Cloud)
```bash
python train_stair.py
```
This is a practical starter adaptation: 4-bit Mistral 7B + LoRA r=16/alpha=32, 4096-token max sequence. It is not a verified exact reproduction of the paper and does not include a trained adapter.

## Run app
```bash
streamlit run app.py
```
Upload a different judgment PDF. Add Streamlit Secrets:
```toml
OPENROUTER_API_KEY = "..."
OPENROUTER_MODEL = "openai/gpt-4o-mini"
```
For deployment, train the adapter in Colab and store it in model storage; load it in Streamlit. Do not download the full Kaggle corpus or train Mistral on every app start.

## Limitations
No trained model included; embedding fallback is only a baseline. Heuristic ToC extraction requires manual review. Page labels are based on extracted PDF page boundaries. Not legal advice; verify answers against the original judgment.
