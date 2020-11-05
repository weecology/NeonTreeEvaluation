from deepforest import deepforest
import pandas as pd
import glob

model = deepforest.deepforest()
model.use_release()

files = glob.glob("/orange/ewhite/b.weinstein/NeonTreeEvaluation/pretraining/crops/*.jpg")
results = []
for x in files:
    boxes = model.predict_image(x, return_plot = False)
    boxes["file"] = x
    results.append(boxes)

results = pd.concat(results)
results.to_csv("predictions.csv")
