# ========== CONFIG ==========
take = 999

# ========== CODE ==========
import os, pymongo, json
from algorithms.hanoi import extract_feature_from_file
import numpy as np
from bson.objectid import ObjectId

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["msee"]
mycol = mydb["songs"]


def save_features_and_labels(
    features, labels, features_file="hanoi_features.npy", labels_file="hanoi_labels.npy"
):
    models_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../models/")
    )
    features_path = os.path.join(models_folder, features_file)
    labels_path = os.path.join(models_folder, labels_file)
    np.save(features_path, features)
    np.save(labels_path, labels)


music_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../public/music")
)

count = 0
len = len(os.listdir(music_folder))


for filename in os.listdir(music_folder):
    count += 1
    if filename.endswith(".mp3"):
        file_path = os.path.join(music_folder, filename)
        features = extract_feature_from_file(file_path)
        mycol.update_one(
            {"_id": ObjectId(filename.split(".")[0])},
            {"$set": {"hanoi_features": np.array(features).tolist(), "status": 2}},
        )
        print(f"{count}/{take}/{len}: Done - {filename}")
    else:
        print(f"{count}/{take}/{len}: Skipped - {filename}")
    if count >= take:
        break

# Convert lists to NumPy arrays
# features_array = np.array(all_features).astype("float32")
# labels_array = np.array(all_labels)

# save_features_and_labels(features_array, labels_array)
