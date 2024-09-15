import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libs.mongo import hcm_features, songs
import librosa
import numpy as np
import hashlib
from scipy.signal import find_peaks
import time

count = -1


def create_constellation_map(spectrogram, k_max=3, percentile_threshold=99):
    constellation_map = []
    for i in range(spectrogram.shape[1]):
        time_slice = spectrogram[:, i]
        threshold = np.percentile(time_slice, percentile_threshold)
        peaks, _ = find_peaks(time_slice, distance=20, height=threshold)
        top_peaks = sorted(peaks, key=lambda x: time_slice[x], reverse=True)[:k_max]
        for peak in top_peaks:
            constellation_map.append((i, peak))
    return constellation_map


def create_hashes(constellation_map, fan_out=15, delta_time=0.5):
    hashes = []
    for i, anchor in enumerate(constellation_map[:-fan_out]):
        for j in range(1, min(fan_out, len(constellation_map) - i)):
            point = constellation_map[i + j]
            t1, f1 = anchor
            t2, f2 = point

            if t2 - t1 <= delta_time:
                h = hashlib.sha1(f"{f1}|{f2}|{t2-t1}".encode()).hexdigest()[:10]
                hashes.append((h, int(t1 * 10) / 10))

    return hashes


def create_database_index(hashes, song_idn):
    chunk_size = 100000
    for i in range(0, len(hashes), chunk_size):
        chunk = hashes[i : i + chunk_size]
        features = {
            "song_idn": song_idn,
            "chunk_id": i // chunk_size,
            "hashes": [(h, int(t)) for h, t in chunk],
        }
        hcm_features.insert_one(features)


def process_song(song, index):
    start_time = time.time()
    song_id = str(song["_id"])
    file_path = f"public/music/{song_id}.mp3"

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False

    audio, sr = librosa.load(file_path, mono=True)
    stft = librosa.stft(audio)
    spectrogram = librosa.amplitude_to_db(np.abs(stft), ref=np.max)

    constellation_map = create_constellation_map(spectrogram)
    hashes = create_hashes(constellation_map)

    create_database_index(hashes, song["idn"])

    songs.update_one({"_id": song["_id"]}, {"$set": {"status": 2}})

    end_time = time.time()
    processing_time = end_time - start_time

    print(
        f"[{index}] Processed: {song['title']}, Category: {song.get('category')}, "
        f"SR: {sr}, Duration: {len(audio)/sr:.2f}s, "
        f"Constellation points: {len(constellation_map)}, Hashes: {len(hashes)}, "
        f"Processing time: {processing_time:.2f}s"
    )

    return True


def main():
    processed = 0
    while count == -1 or processed < count:
        song = songs.find_one({"status": 1})
        if not song:
            print("No more songs to process")
            break

        if process_song(song, processed + 1):
            processed += 1

        if count != -1 and processed >= count:
            break


if __name__ == "__main__":
    main()
