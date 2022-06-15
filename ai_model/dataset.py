import pandas as pd

import torch
from torch.utils.data import Dataset

from utils import get_label_num

class TensorFeatures(object):
    def __init__(self):
        self.input_ids = []
        self.attention_mask = []
        self.label_ids = []
    
    def add_feature(self, input_ids, attention_mask, label_ids):
        self.input_ids.append(self._to_tensor(input_ids))
        self.attention_mask.append(self._to_tensor(attention_mask))
        self.label_ids.append(self._to_tensor(label_ids))
    
    def _to_tensor(self, input_list):
        return torch.tensor(input_list, dtype=torch.long)
    
    def __getitem__(self, idx):
        return self.input_ids[idx], self.attention_mask[idx], self.label_ids[idx]
    
    def __len__(self):
        return len(self.input_ids)


class CardSequenceDataset(Dataset):
    def __init__(self, args, file_path, tokenizer):
        self.max_len = args.max_len
        self.feature = self._preprocess(tokenizer, file_path)

    def _file_preprocess(self, file_path):
        df = pd.read_csv(file_path, sep='\t', header=None, names=['sentence', 'tag'])
        sentence = df['sentence'].map(lambda x: x.strip().split())
        label = df['tag'].map(lambda x: x.split())
        return sentence, label
    
    def _preprocess(self, tokenizer, file_path):
        sentence_list, label_name_list = self._file_preprocess(file_path)
        pad_token_label_id = torch.nn.CrossEntropyLoss().ignore_index

        features = TensorFeatures()
        for sentence, label_name in zip(sentence_list, label_name_list):
            tokens = []
            label_ids = []

            assert len(sentence) == len(label_name), f"문장 단어수와 BIO Tag 개수가 다릅니다.(문장 단어:{len(sentence)}/BIO Tag:{len(label_name)})"
            
            for word, label in zip(sentence, label_name):
                word_tokens = tokenizer.tokenize(word)
                if not word_tokens:
                    word_tokens = [tokenizer.unk_token]
                tokens.extend(word_tokens)

                label_ids.extend([get_label_num(label)] + [pad_token_label_id] * (len(word_tokens) - 1))

            if len(tokens) > (self.max_len - 2):
                empty_len = self.max_len - 2
                tokens = tokens[: empty_len]
                label_ids = label_ids[: empty_len]

            tokens += [tokenizer.sep_token]
            label_ids += [pad_token_label_id]

            tokens = [tokenizer.cls_token] + tokens
            label_ids = [pad_token_label_id] + label_ids

            input_ids = tokenizer.convert_tokens_to_ids(tokens)
            attention_mask = [1] * len(input_ids)

            pad_len = self.max_len - len(input_ids)
            input_ids = input_ids + ([tokenizer.pad_token_id] * pad_len)
            attention_mask = attention_mask + ([0] * pad_len)
            label_ids = label_ids + ([pad_token_label_id] * pad_len)

            features.add_feature(input_ids, attention_mask, label_ids)
        
        return features

    def __getitem__(self, idx):
        return self.feature[idx]

    def __len__(self):
        return len(self.feature)
