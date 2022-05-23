import time
import os
import random
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import sys
from utils import *

import argparse

parser = argparse.ArgumentParser(description='예시')
parser.add_argument('--font_path', type=str, default='./font')
parser.add_argument('--logo_path', type=str, default='./logo')
parser.add_argument('--out_dir', type=str, default='./namecards')
parser.add_argument('--num', type=int, default=10)

# opt는 parser로 나눈 모든 argument들을 dict 형식으로 가진다.
args = parser.parse_args()

make_namecard_h(args)        
