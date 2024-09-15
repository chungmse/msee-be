import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import librosa
import time
import numpy as np
from bson import ObjectId
from libs.mongo import jobs
from libs.rabbitmq import recognize_channel
from algorithms.hcm import (
    create_constellation_map,
    create_hashes,
    find_matches,
    align_matches,
)


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
    return enumerate(sorted_songs[:5], 1), processing_time


def callback(ch, method, properties, body):
    body = body.decode("utf-8")
    print("=========================================")
    print(f"Received job_id: {body}")
    this_job = jobs.find_one({"_id": ObjectId(body), "status": "waiting"})
    if this_job is None:
        print("Job not found or already processed.")
        return
    print("Processing job...")
    jobs.update_one({"_id": ObjectId(body)}, {"$set": {"status": "processing"}})
    top5, time = recognize_song(f"tmp/{body}.wav")
    list_result = []
    print("Top 5 matches:")
    for i, (song_idn, score) in top5:
        list_result.append({"song_idn": song_idn, "score": score})
        print(f"{i}. song_idn: {song_idn}, score: {score}")
    print("Time:", time)
    jobs.update_one(
        {"_id": ObjectId(body)},
        {
            "$set": {
                "status": "completed",
                "result": list_result,
                "processing_time": time,
            }
        },
    )
    os.remove(f"tmp/{body}.wav")
    print("Job done!")


recognize_channel.basic_consume(
    queue="recognize", on_message_callback=callback, auto_ack=True
)

print("Waiting for jobs...")

recognize_channel.start_consuming()
