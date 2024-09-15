from pymongo import MongoClient
import redis

# Kết nối MongoDB
mongo_client = MongoClient("localhost", 27017)
msee_db = mongo_client["msee"]
hcm_features = msee_db["hcm_features"]
songs = msee_db["songs"]  # Thêm collection songs

hcm_features.create_index("song_idn")

# Kết nối Redis
redis_client = redis.Redis(host="localhost", port=6379, db=3)


def reset_databases():
    # Reset MongoDB collection hcm_features
    result = hcm_features.delete_many({})
    print(
        f"Đã xóa {result.deleted_count} documents từ MongoDB collection 'hcm_features'"
    )

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

    # Đóng kết nối
    mongo_client.close()
    redis_client.close()
