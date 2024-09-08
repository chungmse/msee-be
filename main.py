import os
import numpy as np
import librosa
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from collections import Counter
from algorithms.hanoi import extract_features, crop_feature


def load_features_and_labels(
    features_file="hanoi_features.npy", labels_file="hanoi_labels.npy"
):
    models_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "models/"))
    features_path = os.path.join(models_folder, features_file)
    labels_path = os.path.join(models_folder, labels_file)
    features = np.load(features_path)
    labels = np.load(labels_path)
    return features, labels


# Check and load data if it already exists
features_array, labels_array = load_features_and_labels()

# Data preprocessing
scaler = StandardScaler()
pca = PCA(n_components=50)
knn = KNeighborsClassifier(n_neighbors=5)

pipeline = make_pipeline(scaler, pca, knn)
pipeline.fit(features_array, labels_array)

# Processing the recording file
y, sr = librosa.load("output.wav", sr=44100)
y = librosa.util.normalize(y)
feat = extract_features(y, sr)

results = []
for i in range(0, feat.shape[0] - 10, 10):  # Adjust step size
    crop_feat = crop_feature(feat, i, nb_step=10)
    crop_feat = np.array(crop_feat).astype("float32").reshape(1, -1)
    # Predict with KNN
    pred = pipeline.predict(crop_feat)
    results.append(pred[0])

# Calculate the frequency of each song occurrence
results = np.array(results)
most_song = Counter(results)
print(most_song.most_common())
