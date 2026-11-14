import json,torch
from datasets import Dataset
from transformers import AutoTokenizer,AutoModelForCausalLM,TrainingArguments
from peft import LoraConfig
from trl import SFTTrainer
BASE="mistralai/Mistral-7B-Instruct-v0.2"
rows=[]
for line in open("data/stair_train.jsonl",encoding="utf8"):
    x=json.loads(line); toc="\n".join("- "+t for t in x["toc"])
    prompt=("You are a structure-aware legal retriever. Given question and complete judgment ToC, "
    "output ONLY the exact most relevant leaf section title.\nTOC:\n"+toc+"\nQUESTION: "+x["question"]+"\nSECTION: "+x["gold_leaf"])
    rows.append({"text":prompt})
tok=AutoTokenizer.from_pretrained(BASE)
if tok.pad_token is None: tok.pad_token=tok.eos_token
model=AutoModelForCausalLM.from_pretrained(BASE,device_map="auto",torch_dtype=torch.float16,load_in_4bit=True)
peft=LoraConfig(r=16,lora_alpha=32,lora_dropout=.05,bias="none",task_type="CAUSAL_LM",target_modules=["q_proj","k_proj","v_proj","o_proj"])
args=TrainingArguments(output_dir="artifacts/supreme-court-stair",num_train_epochs=1,per_device_train_batch_size=1,gradient_accumulation_steps=8,learning_rate=2e-4,logging_steps=5,save_strategy="epoch",fp16=True,report_to="none",gradient_checkpointing=True)
trainer=SFTTrainer(model=model,args=args,train_dataset=Dataset.from_list(rows),peft_config=peft,processing_class=tok,max_seq_length=4096)
trainer.train(); trainer.save_model("artifacts/supreme-court-stair"); tok.save_pretrained("artifacts/supreme-court-stair")
