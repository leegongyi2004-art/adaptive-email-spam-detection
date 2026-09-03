"""Fine-tune an open-weight Transformer from a reviewed raw_email,label CSV."""
from __future__ import annotations
import argparse, csv, json, random
from pathlib import Path
from .transformer import TransformerEmailDetector

def main():
    parser = argparse.ArgumentParser(description="Fine-tune DistilBERT locally for ham/spam classification.")
    parser.add_argument("csv", help="Reviewed CSV with raw_email,label (0=ham, 1=spam)")
    parser.add_argument("--output", default="models/distilbert-email")
    parser.add_argument("--base-model", default="distilbert-base-uncased")
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--epochs", type=float, default=3)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    try:
        import torch
        from datasets import Dataset
        from transformers import AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding, Trainer, TrainingArguments
    except ImportError as e: raise SystemExit("Install requirements-transformer.txt first.") from e
    with open(args.csv, encoding="utf-8", newline="") as f: rows = list(csv.DictReader(f))
    if len(rows) < 20 or {r.get("label") for r in rows} != {"0", "1"}:
        raise SystemExit("Need at least 20 reviewed rows and both labels 0 and 1.")
    random.Random(args.seed).shuffle(rows)
    cut = max(1, int(len(rows) * .1)); validation, training = rows[:cut], rows[cut:]
    def dataset(rows): return Dataset.from_dict({"text": [TransformerEmailDetector.email_text(r["raw_email"]) for r in rows], "labels": [int(r["label"]) for r in rows]})
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    def tokenize(batch): return tokenizer(batch["text"], truncation=True, max_length=args.max_length)
    train, valid = dataset(training).map(tokenize, batched=True), dataset(validation).map(tokenize, batched=True)
    model = AutoModelForSequenceClassification.from_pretrained(args.base_model, num_labels=2)
    train_args = TrainingArguments(output_dir=args.output + "-checkpoints", learning_rate=args.learning_rate,
      per_device_train_batch_size=args.batch_size, per_device_eval_batch_size=args.batch_size, num_train_epochs=args.epochs,
      weight_decay=.01, warmup_ratio=.1, eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True,
      metric_for_best_model="eval_loss", logging_strategy="epoch", report_to=[] , seed=args.seed)
    trainer = Trainer(model=model, args=train_args, train_dataset=train, eval_dataset=valid,
      processing_class=tokenizer, data_collator=DataCollatorWithPadding(tokenizer=tokenizer))
    trainer.train(); metrics = trainer.evaluate()
    Path(args.output).mkdir(parents=True, exist_ok=True); trainer.save_model(args.output); tokenizer.save_pretrained(args.output)
    Path(args.output, "training_config.json").write_text(json.dumps(vars(args) | {"validation_rows": len(validation), "training_rows": len(training), "metrics": metrics, "device": "cuda" if torch.cuda.is_available() else "cpu"}, indent=2, default=float))
    print(json.dumps(metrics, indent=2)); print("Saved model to", args.output)
if __name__ == "__main__": main()
