import numpy as np
import torch
from PIL import Image
from io import BytesIO
import dotenv
from transformers import AutoProcessor, Pix2StructForConditionalGeneration
import transformers

dotenv.load_dotenv()
transformers.logging.set_verbosity_info()
device = "cuda:0" if torch.cuda.is_available() else "cpu"

processor = AutoProcessor.from_pretrained("google/pix2struct-textcaps-base")
model = Pix2StructForConditionalGeneration.from_pretrained("google/pix2struct-textcaps-base").to(device)

image = Image.open(open("demos/p2.png", "rb"))

while True:
    inputs = processor(text=input("  > "), images=image, return_tensors="pt", add_special_tokens=False).to(device)

    generated_ids = model.generate(**inputs, max_new_tokens=1024)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(generated_text)
