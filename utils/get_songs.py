from selenium import webdriver
import pymongo, json

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["msee"]
mycol = mydb["songs"]

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

categories = [
    (
        "Nhạc Trẻ",
        "https://zingmp3.vn/album/Top-100-Bai-Hat-Nhac-Tre-Hay-Nhat-Jack-J97-Quang-Hung-MasterD-Noo-Phuoc-Thinh-Ho-Quang-Hieu/ZWZB969E.html",
    ),
    (
        "Nhạc Trịnh",
        "https://zingmp3.vn/album/Top-100-Nhac-Trinh-Hay-Nhat-Hung-Cuong-Luu-Anh-Loan-Viet-Hoa-Anh-Trinh/ZWZB96A9.html",
    ),
    (
        "Nhạc Thiếu Nhi",
        "https://zingmp3.vn/album/Top-100-Nhac-Thieu-Nhi-Hay-Nhat-Ngoc-Khanh-Chi-Be-Thanh-Ngan-Chan-Be-Minh-Vy/ZWZB96A6.html",
    ),
    (
        "Nhạc Trữ Tình",
        "https://zingmp3.vn/album/Top-100-Nhac-Tru-Tinh-Hay-Nhat-Quynh-Trang-Duong-Hong-Loan-Manh-Quynh-Luu-Anh-Loan/ZWZB969F.html",
    ),
    (
        "Nhạc Rap Việt",
        "https://zingmp3.vn/album/Top-100-Nhac-Rap-Viet-Nam-Hay-Nhat-HIEUTHUHAI-Rhyder-Bray-Double2T/ZWZB96AI.html",
    ),
    (
        "Nhạc Phim Việt",
        "https://zingmp3.vn/album/Top-100-Nhac-Phim-Viet-Nam-Hay-Nhat-Phan-Manh-Quynh-Lam-Bao-Ngoc-Khai-Dang-Chi-Pu/ZWZB96AA.html",
    ),
    (
        "Nhạc Hoa",
        "https://zingmp3.vn/album/Top-100-Nhac-Hoa-Hay-Nhat-Mong-Nhien-Danh-Quyet-Tinh-Lung-Cuc-Tinh-Y/ZWZB96EI.html",
    ),
    (
        "Nhạc Hàn",
        "https://zingmp3.vn/album/Top-100-Nhac-Han-Quoc-Hay-Nhat-BABYMONSTER-ILLIT-aespa-BLACKPINK/ZWZB96DC.html",
    ),
]

count_all = 0

for cat in categories:
    cat_name = cat[0]
    cat_url = cat[1]
    driver.get_log("performance")
    driver.get(cat_url)
    logs = driver.get_log("performance")
    api_url = None
    count_cat = 0
    for entry in logs:
        log = entry["message"]
        if "api/v2/page/get/playlist?id=" in log:
            log_json = json.loads(log)
            url = (
                log_json.get("message", {})
                .get("params", {})
                .get("response", {})
                .get("url")
            )
            if isinstance(url, str) and "api/v2/page/get/playlist?id=" in url:
                api_url = url
                break

    if api_url is None:
        print(f"No API: {cat_name}")
        continue

    driver.get(api_url)

    api_url_data = json.loads(driver.find_element(by="tag name", value="pre").text)

    for song in api_url_data["data"]["song"]["items"]:
        count_all += 1
        count_cat += 1
        song["category"] = cat_name
        song["status"] = 0
        result = mycol.update_one(
            {"encodeId": song["encodeId"]},
            {
                "$setOnInsert": song,
            },
            upsert=True,
        )
        if result.upserted_id is not None:
            print(f"{count_all} | {count_cat} | {cat_name} | Inserted: {song['title']}")
        else:
            print(
                f"{count_all} | {count_cat} | {cat_name} | Duplicate: {song['title']}"
            )

driver.quit()
