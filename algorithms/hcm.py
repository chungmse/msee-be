import numpy as np
import hashlib
from collections import defaultdict
from scipy.signal import find_peaks
from libs.redis import redis_client


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
