import random
import torch
import numpy as np

from kobert_tokenizer import KoBERTTokenizer
from seqeval.metrics import precision_score, recall_score, f1_score

NER_TAG = ['UNK', 'O', 'PER-B', 'PER-I', 'PER_E-B', 'PER_E-I', 'NUM-B', 'NUM-I',
           'TEL-B', 'TEL-I', 'FAX-B', 'FAX-I', 'MAIL-B', 'MAIL-I', 'POS-B', 'POS-I','ADD-B', 'ADD-I']

def load_tokenizer(model_path):
    return KoBERTTokenizer.from_pretrained(model_path)

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def get_label_cnt():
    return len(NER_TAG)

def get_label_name(class_num):
    return NER_TAG[class_num]

def get_label_num(class_name):
    return NER_TAG.index(class_name)

def compute_metrics(labels, preds):
    assert len(preds) == len(labels)
    return f1_pre_rec(labels, preds)

def f1_pre_rec(labels, preds):
    return {
        "precision": precision_score(labels, preds, suffix=True),
        "recall": recall_score(labels, preds, suffix=True),
        "f1": f1_score(labels, preds, suffix=True, average='micro')
    }
