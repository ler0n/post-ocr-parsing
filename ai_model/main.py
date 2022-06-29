import os
import pickle
import argparse

import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler
from utils import load_tokenizer, set_seed
from dataset import CardSequenceDataset
from model import CardNERClassifier

def main(args):
    set_seed(args.seed)
    tokenizer = load_tokenizer(args.model_path)

    # set trainset
    train_dataset = CardSequenceDataset(args, args.train_file, tokenizer)
    train_sampler = RandomSampler(train_dataset)
    train_loader = DataLoader(train_dataset, sampler=train_sampler, batch_size=args.train_batch_size, num_workers=4)

    args.t_total = len(train_loader) // args.gradient_accumulation_steps * args.num_train_epochs

    #set validset
    val_dataset = CardSequenceDataset(args, args.test_file, tokenizer)
    val_sampler = SequentialSampler(val_dataset)
    val_loader = DataLoader(val_dataset, sampler=val_sampler, batch_size=args.eval_batch_size, num_workers=2)

    with open(os.path.join(args.model_dir, 'args.pickle'), 'wb') as f:
        pickle.dump(args, f)
    
    model = CardNERClassifier(args)
    checkpoint_callback = ModelCheckpoint(dirpath=args.model_dir, save_top_k=1, monitor="f1")

    trainer = pl.Trainer(accelerator="gpu", devices=1, \
                         max_epochs=args.num_train_epochs, 
                         callbacks=[checkpoint_callback])
    trainer.fit(model, train_loader, val_loader)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--task", default="card-ner", type=str, help="The name of the task to train")
    parser.add_argument("--model_dir", default="./model", type=str, help="Path to save, load model")
    parser.add_argument("--model_path", default='skt/kobert-base-v1')

    parser.add_argument("--train_file", default="train.tsv", type=str, help="Train file")
    parser.add_argument("--test_file", default="test.tsv", type=str, help="Test file")

    parser.add_argument('--seed', type=int, default=42, help="random seed for initialization")
    parser.add_argument("--train_batch_size", default=32, type=int, help="Batch size for training.")
    parser.add_argument("--eval_batch_size", default=64, type=int, help="Batch size for evaluation.")
    parser.add_argument("--max_len", default=50, type=int, help="The maximum total input sequence length after tokenization.")
    parser.add_argument("--learning_rate", default=5e-5, type=float, help="The initial learning rate for Adam.")
    parser.add_argument("--num_train_epochs", default=4, type=int, help="Total number of training epochs to perform.")
    parser.add_argument('--gradient_accumulation_steps', type=int, default=1,
                        help="Number of updates steps to accumulate before performing a backward/update pass.")
    parser.add_argument("--weight_decay", default=0.0, type=float, help="Weight decay if we apply some.")
    parser.add_argument("--adam_epsilon", default=1e-8, type=float, help="Epsilon for Adam optimizer.")
    parser.add_argument("--max_grad_norm", default=1.0, type=float, help="Max gradient norm.")
    parser.add_argument("--warmup_steps", default=0, type=int, help="Linear warmup over warmup_steps.")

    args = parser.parse_args()
    main(args)
