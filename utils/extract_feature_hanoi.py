import os, pymongo
from algorithms.hanoi import extract_feature_from_file
import numpy as np


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["msee"]
mycol = mydb["songs"]

count = 0

music_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../public/music")
)

features_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../features/hanoi")
)


def extract_feature():
    global count
    count += 1
    # Find a song to extract feature
    song = mycol.find_one({"status": 1})
    if song is None:
        print(f"{count} | No song to extract feature")
        exit()
    file_path = os.path.join(music_folder, str(song.get("_id")) + ".mp3")
    if not os.path.exists(file_path):
        print(f"{count} | No file: {song['title']} - {song['_id']}")
        return
    features = np.array(extract_feature_from_file(file_path)).astype("float32")
    features_path = os.path.join(features_folder, str(song.get("_id")) + ".npy")
    np.save(features_path, features)
    mycol.update_one(
        {"_id": song.get("_id")},
        {"$set": {"status": 2}},
    )
    print(f"{count}: Done - {str(song.get("_id"))} - {song.get('title')} - {song.get('category')}")


while True:
    extract_feature()
