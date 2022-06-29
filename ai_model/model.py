import torch
from torch.optim import AdamW

import pytorch_lightning as pl

from transformers import BertForTokenClassification, BertConfig
from transformers import get_linear_schedule_with_warmup

from utils import cal_metrics, get_label_name, get_label_cnt

class CardNERClassifier(pl.LightningModule):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.pad_token_label_id = torch.nn.CrossEntropyLoss().ignore_index
        config = BertConfig.from_pretrained(args.model_path, num_labels=get_label_cnt())
        self.ner_classifier = BertForTokenClassification.from_pretrained(args.model_path, config=config)

    def forward(self, x):
        inputs = {'input_ids': x[0], 'attention_mask': x[1]}
        pred = self.ner_classifier(**inputs)
        return pred

    def training_step(self, batch, batch_idx):
        inputs = {'input_ids': batch[0], 'attention_mask': batch[1], 'labels': batch[2]}
        out = self.ner_classifier(**inputs)
        loss = out[0]
        self.log('loss', loss, on_step=True, on_epoch=True, prog_bar=True)
        return loss

    def validation_step(self, val_batch, batch_idx):
        inputs = {'input_ids': val_batch[0], 'attention_mask': val_batch[1], 'labels': val_batch[2]}
        out = self.ner_classifier(**inputs)
        loss = out[0]
        preds = out[1].argmax(axis=2)
        pred_list = []
        label_list = []
        for i in range(inputs['labels'].shape[0]):
            for j in range(inputs['labels'].shape[1]):
                if inputs['labels'][i][j] != self.pad_token_label_id:
                    label_list.append(get_label_name(inputs['labels'][i][j]))
                    pred_list.append(get_label_name(preds[i][j]))

        return pred_list, label_list, loss
    
    def test_step(self, test_batch, batch_idx):
        inputs = {'input_ids': test_batch[0], 'attention_mask': test_batch[1], 'labels': test_batch[2]}
        output = self.ner_classifier(inputs)
        preds = output[1].argmax(axis=2).detach().cpu().numpy()
        return {'prediction': preds}

    def configure_optimizers(self):
        train_parameter = self.parameters()
        
        optimizer = AdamW(train_parameter, lr=self.args.learning_rate, eps=self.args.adam_epsilon)
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=self.args.warmup_steps, num_training_steps=self.args.t_total)
        return [optimizer], [scheduler]
    
    def validation_epoch_end(self, outputs):
        val_loss = 0
        pred_list = []
        label_list = []
        
        for pred, truth, loss in outputs:
            val_loss += loss
            pred_list.append(pred)
            label_list.append(truth)
        
        result = cal_metrics(label_list, pred_list)
        result['val_loss'] = val_loss / len(outputs)
        self.log('loss', loss, on_step=False, on_epoch=True, prog_bar=True)
        self.log_dict(result)
    