from selenium import webdriver
import os, requests, json, pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["msee"]
songs = mydb["songs"]

count = 0


def download_song():
    global count
    count += 1
    # Init
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    options.add_argument("--incognito")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    # Find a song to download
    song = songs.find_one({"status": 0})
    if song is None:
        print(f"{count} | No song to download")
        driver.quit()
        exit()
    # Load web & find mp3 link
    mp3_url = None
    driver.get_log("performance")
    driver.get("https://zingmp3.vn" + song["link"])
    logs = driver.get_log("performance")
    for entry in logs:
        log = entry["message"]
        if "Media" in log:
            log_json = json.loads(log)
            url = (
                log_json.get("message", {})
                .get("params", {})
                .get("response", {})
                .get("url")
            )
            if isinstance(url, str) and "?authen=exp=" in url:
                mp3_url = url
                break

    if mp3_url is None:
        print(f"{count} | No link: {song['title']} - {song['_id']}")
        return

    response = requests.get(url, stream=True)
    file_path = os.path.join("public/music", f"{song['_id']}.mp3")
    file_path = os.path.abspath(file_path)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"{count} | Downloaded: {song['title']} - {song['_id']}.mp3")
        songs.update_one({"_id": song["_id"]}, {"$set": {"status": 1}})
    else:
        print(f"{count} |Error: {song['title']} - {song['_id']}")

    driver.quit()


while True:
    download_song()
