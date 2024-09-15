import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libs.mongo import hcm_features
from libs.redis import redis_client

import time
from multiprocessing import Pool, cpu_count


def empty_redis_db():
    redis_client.flushdb()
    print("Redis database has been emptied.")


def process_song(song_idn):
    pipeline = redis_client.pipeline()
    for feature in hcm_features.find({"song_idn": song_idn}):
        for h, t in feature["hashes"]:
            pipeline.sadd(h, f"{song_idn}:{t}")
    pipeline.execute()
    return f"Processed song {song_idn}"


def create_caches():
    start_time = time.time()
    song_idns = hcm_features.distinct("song_idn")
    total_songs = len(song_idns)
    with Pool(processes=cpu_count()) as pool:
        for i, result in enumerate(pool.imap_unordered(process_song, song_idns), 1):
            print(f"{result} - {i}/{total_songs}")
    end_time = time.time()
    processing_time = end_time - start_time
    print(f"Cache creation completed. Total time: {processing_time:.2f}s")
    print(f"Total songs processed: {total_songs}")


if __name__ == "__main__":
    empty_redis_db()
    create_caches()
