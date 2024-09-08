import numpy as np
import librosa
from python_speech_features import mfcc, delta


def extract_features(y, sr=44100):
    # Extract MFCC, Delta MFCC, and Delta-Delta MFCC
    mfcc_features = mfcc(y, sr, numcep=13, nfft=2048)
    delta_features = delta(mfcc_features, N=2)
    delta_delta_features = delta(delta_features, N=2)

    # Extract additional features
    chroma_features = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=2048)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr, n_fft=2048)
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y=y)
    tonnetz_features = librosa.feature.tonnetz(y=y, sr=sr)
    rmse = librosa.feature.rms(y=y)
    spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048)
    spectral_flatness = librosa.feature.spectral_flatness(y=y, n_fft=2048)

    # Ensure all features have the same number of frames (n_frames)
    n_frames = mfcc_features.shape[0]

    def pad_or_truncate(arr, length):
        if arr.shape[1] < length:
            return np.pad(arr, ((0, 0), (0, length - arr.shape[1])), mode="constant")
        else:
            return arr[:, :length]

    chroma_features = pad_or_truncate(chroma_features, n_frames)
    spectral_contrast = pad_or_truncate(spectral_contrast, n_frames)
    zero_crossing_rate = pad_or_truncate(zero_crossing_rate, n_frames)
    tonnetz_features = pad_or_truncate(tonnetz_features, n_frames)
    rmse = pad_or_truncate(rmse, n_frames)
    spectrogram = pad_or_truncate(spectrogram, n_frames)
    spectral_flatness = pad_or_truncate(spectral_flatness, n_frames)

    # Combine all features
    features = np.hstack(
        (
            mfcc_features,
            delta_features,
            delta_delta_features,
            chroma_features.T,
            spectral_contrast.T,
            zero_crossing_rate.T,
            tonnetz_features.T,
            rmse.T,
            spectrogram.T,
            spectral_flatness.T,
        )
    )
    return features


def crop_feature(feat, i=0, nb_step=10, maxlen=100):
    # Ensure index is non-negative and within bounds
    i = max(0, i)
    end_index = min(i + nb_step, feat.shape[0])
    crop_feat = np.array(feat[i:end_index]).flatten()

    # Handle case where crop_feat is shorter than maxlen
    if len(crop_feat) < maxlen:
        crop_feat = np.pad(crop_feat, (0, maxlen - len(crop_feat)), mode="constant")
    else:
        crop_feat = crop_feat[:maxlen]  # Truncate if longer than maxlen

    return crop_feat


def extract_feature_from_file(file_path):
    features = []
    y, sr = librosa.load(file_path, sr=44100)
    feat = extract_features(y, sr)
    for i in range(0, feat.shape[0] - 10, 5):
        features.append(crop_feature(feat, i, nb_step=10))
    return features
