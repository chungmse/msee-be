import librosa
import numpy as np
from pymongo import MongoClient
import redis
import time
from collections import defaultdict
from algorithms.hcm import create_constellation_map, create_hashes

mongo_client = MongoClient("localhost", 27017)
msee_db = mongo_client["msee"]
songs = msee_db["songs"]

redis_client = redis.Redis(host="localhost", port=6379, db=3)


def find_matches(sample_hashes):
    matches = defaultdict(list)
    for h, t in sample_hashes:
        matching_entries = redis_client.smembers(h)
        for entry in matching_entries:
            song_idn, time = entry.decode().split(":")
            matches[song_idn].append((int(time), t))
    return matches


def align_matches(matches):
    song_scores = defaultdict(int)

    for song_idn, time_pairs in matches.items():
        diff_counter = defaultdict(int)
        for db_time, sample_time in time_pairs:
            diff = sample_time - db_time
            diff_counter[diff] += 1

        song_scores[song_idn] = max(diff_counter.values())

    return sorted(song_scores.items(), key=lambda x: x[1], reverse=True)


def recognize_song(file_path):
    start_time = time.time()

    audio, sr = librosa.load(file_path, sr=22050, mono=True)
    stft = librosa.stft(audio)
    spectrogram = librosa.amplitude_to_db(np.abs(stft), ref=np.max)

    peaks = create_constellation_map(spectrogram)
    sample_hashes = create_hashes(peaks)

    matches = find_matches(sample_hashes)
    sorted_songs = align_matches(matches)

    end_time = time.time()
    processing_time = end_time - start_time

    print("Top 10 matches:")
    for i, (song_idn, match_count) in enumerate(sorted_songs[:10], 1):
        song = songs.find_one({"idn": int(song_idn)})
        if song:
            print(
                f"{i}. Recognized: {song['title']} - {song.get('category')} | Match: {match_count}"
            )
        else:
            print(
                f"{i}. Song Idn: {song_idn} | Match: {match_count} (Not found in database)"
            )

    print(f"\nProcessing time: {processing_time:.2f}s")


if __name__ == "__main__":
    sample_path = "utils/output.wav"
    recognize_song(sample_path)

mongo_client.close()
redis_client.close()
