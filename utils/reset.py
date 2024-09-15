import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libs.mongo import hcm_features, songs, jobs
from libs.redis import redis_client


def reset_databases():
    # Reset MongoDB collection hcm_features
    result = hcm_features.delete_many({})
    print(
        f"Đã xóa {result.deleted_count} documents từ MongoDB collection 'hcm_features'"
    )

    # Reset MongoDB collection jobs
    result_jobs = jobs.delete_many({})
    print(f"Đã xóa {result_jobs.deleted_count} documents từ MongoDB collection 'jobs'")

    # Reset Redis database
    redis_client.flushdb()
    print("Đã xóa tất cả keys từ Redis database 3")

    # Cập nhật tất cả bản ghi trong collection songs về status = 1
    update_result = songs.update_many({}, {"$set": {"status": 1}})
    print(
        f"Đã cập nhật {update_result.modified_count} bản ghi trong collection 'songs' về status = 1"
    )


if __name__ == "__main__":
    reset_databases()
    print("Reset và cập nhật hoàn tất.")
