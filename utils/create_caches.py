from pymongo import MongoClient
import redis
import time
from multiprocessing import Pool, cpu_count

mongo_client = MongoClient("localhost", 27017)
msee_db = mongo_client["msee"]
hcm_features = msee_db["hcm_features"]

redis_client = redis.Redis(host="localhost", port=6379, db=3)


def empty_redis_db():
    redis_client.flushdb()
    print("Redis database has been emptied.")


def process_song(song_idn):
    local_redis = redis.Redis(host="localhost", port=6379, db=3)
    pipeline = local_redis.pipeline()

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
    mongo_client.close()
    redis_client.close()
