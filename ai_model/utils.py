import random
import torch

import numpy as np

from kobert_tokenizer import KoBERTTokenizer
from seqeval.metrics import precision_score, recall_score, f1_score

from data import BIO_TAG

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def load_tokenizer(model_name):
    return KoBERTTokenizer.from_pretrained(model_name)

def cal_metrics(labels, preds):
    assert len(preds) == len(labels)
    return f1_pre_rec(labels, preds)

def f1_pre_rec(labels, preds):
    return {
        "precision": precision_score(labels, preds, suffix=True),
        "recall": recall_score(labels, preds, suffix=True),
        "f1": f1_score(labels, preds, suffix=True, average='micro')
    }

def get_label_cnt():
    return len(BIO_TAG)

def get_label_name(class_num):
    return BIO_TAG[class_num]

def get_label_num(class_name):
    return BIO_TAG.index(class_name)
