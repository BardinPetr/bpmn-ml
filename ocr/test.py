from datasetload import load_dataset

rus_ds = [
    "0f4c1460f8077f81230114b6f80e47b418c8f726724924d7409d96302b14992a",
    "042b4c494cf76f0766cc5dce950fd40ae543f396c6bfe16628920027aade322e",
    "6c687fa68107d786a7e386a7e11f32a2789457f7d5a82e0fdacdfb32f432bf27",
    "0f4c1460f8077f81230114b6f80e47b418c8f726724924d7409d96302b14992a",
    "922834786e1189e034d8d4c2ac23a18713f6cc4e02982d77740e2603bade4c40",
    "415b4d5434e47c10cab4056ac4335dce2f9cfcb4ae286a84a1f162c50d6c6cdb",
    "81b4cbf1283147611d05839e6a6c8078aec6c40e40efa2c29f217a38edb46a97",
    "4ac06927a538b76cc9a75c3779dc6ea85ac6b23cf8c8e6a7fac73c20fcb79fc4",
]

data = load_dataset("../transform")
data = [
    (i['image'], i['textdetect'])
    for i in data
    if i['hash'] in rus_ds
]


from paddleocr import PaddleOCR
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)

result = ocr.predict(input=data[0][0])

# Visualize the results and save the JSON results
for res in result:
    res.print()
    res.save_to_img("output")
    res.save_to_json("output")

