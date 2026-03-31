import argparse
import json
import random
import time

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LIST_ENDPOINT = "https://tiki.vn/api/v2/products"
DETAIL_ENDPOINT = "https://tiki.vn/api/v2/products/{product_id}"
CHECKPOINT_FILE = "tiki_checkpoint.json"
BACKUP_FILE = "backup.csv"
OUTPUT_FILE = "products.csv"

# Nhiều danh mục phổ biến để tăng độ phủ dữ liệu
CATEGORY_IDS = [
    8322, 4384, 1883, 1882, 1815, 931, 2549, 1520, 1789, 1703,
    4221, 915, 8594, 27498, 44792, 8400, 8596, 976, 6000, 11612,
]

# Từ khóa phổ biến để quét thêm nếu danh mục bị giới hạn
SEARCH_KEYWORDS = [
    "dien thoai", "laptop", "tai nghe", "sach", "do gia dung",
    "my pham", "thoi trang", "me va be", "do choi", "thuc pham",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}


def create_session():
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=30, pool_maxsize=30)

    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def safe_get_json(session, url, params=None, timeout=20):
    response = session.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def load_checkpoint():
    try:
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "product_ids": [],
            "completed_ids": [],
            "failed_ids": [],
        }


def save_checkpoint(product_ids, completed_ids, failed_ids):
    data = {
        "product_ids": list(product_ids),
        "completed_ids": list(completed_ids),
        "failed_ids": list(failed_ids),
    }
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def extract_category_name(item):
    categories = item.get("categories")
    if isinstance(categories, dict):
        return categories.get("name", "Unknown")
    if isinstance(categories, list) and categories:
        first_category = categories[0]
        if isinstance(first_category, dict):
            return first_category.get("name", "Unknown")
    return "Unknown"


def collect_product_ids(session, target_count, max_pages_per_source=120):
    product_ids = set()
    wanted_ids = int(target_count * 1.4)

    print("--- BƯỚC 1: Thu thập Product IDs ---")

    for category_id in CATEGORY_IDS:
        for page in range(1, max_pages_per_source + 1):
            if len(product_ids) >= wanted_ids:
                return product_ids

            params = {
                "limit": 40,
                "include": "advertisement",
                "category": category_id,
                "page": page,
            }

            try:
                data = safe_get_json(session, LIST_ENDPOINT, params=params).get("data", [])
            except requests.RequestException as error:
                print(f"[WARN] Lỗi danh mục {category_id} trang {page}: {error}")
                time.sleep(random.uniform(1.5, 2.8))
                continue

            if not data:
                break

            for item in data:
                product_id = item.get("id")
                if product_id:
                    product_ids.add(product_id)

            print(
                f"Danh mục {category_id} - Trang {page}: "
                f"{len(product_ids)} IDs độc nhất"
            )
            time.sleep(random.uniform(0.25, 0.6))

    for keyword in SEARCH_KEYWORDS:
        for page in range(1, max_pages_per_source + 1):
            if len(product_ids) >= wanted_ids:
                return product_ids

            params = {
                "limit": 40,
                "q": keyword,
                "page": page,
            }

            try:
                data = safe_get_json(session, LIST_ENDPOINT, params=params).get("data", [])
            except requests.RequestException as error:
                print(f"[WARN] Lỗi keyword '{keyword}' trang {page}: {error}")
                time.sleep(random.uniform(1.5, 2.8))
                continue

            if not data:
                break

            for item in data:
                product_id = item.get("id")
                if product_id:
                    product_ids.add(product_id)

            print(
                f"Keyword '{keyword}' - Trang {page}: "
                f"{len(product_ids)} IDs độc nhất"
            )
            time.sleep(random.uniform(0.25, 0.6))

    return product_ids


def fetch_product_detail(session, product_id):
    url = DETAIL_ENDPOINT.format(product_id=product_id)
    item = safe_get_json(session, url)
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "price": item.get("price", 0),
        "original_price": item.get("original_price", 0),
        "discount_rate": item.get("discount_rate", 0),
        "rating_average": item.get("rating_average", 0),
        "review_count": item.get("review_count", 0),
        "quantity_sold": item.get("quantity_sold", {}).get("value", 0)
        if item.get("quantity_sold")
        else 0,
        "brand": item.get("brand", {}).get("name", "No Brand"),
        "category": extract_category_name(item),
        "url_key": item.get("url_key", ""),
    }


def write_backup(records):
    if records:
        pd.DataFrame(records).drop_duplicates(subset=["id"]).to_csv(
            BACKUP_FILE, index=False, encoding="utf-8-sig"
        )


def scrape_tiki_massive(target_count=10000, max_pages_per_source=120):
    session = create_session()
    checkpoint = load_checkpoint()

    completed_ids = set(checkpoint.get("completed_ids", []))
    failed_ids = set(checkpoint.get("failed_ids", []))
    product_ids = set(checkpoint.get("product_ids", []))

    if len(product_ids) < target_count:
        collected_ids = collect_product_ids(
            session=session,
            target_count=target_count,
            max_pages_per_source=max_pages_per_source,
        )
        product_ids.update(collected_ids)

    print(f"Tổng ID độc nhất hiện có: {len(product_ids)}")

    detailed_data = []
    if completed_ids:
        try:
            existing = pd.read_csv(BACKUP_FILE)
            detailed_data = existing.to_dict(orient="records")
        except (FileNotFoundError, pd.errors.EmptyDataError):
            detailed_data = []

    print("\n--- BƯỚC 2: Tải dữ liệu chi tiết ---")

    available_ids = [product_id for product_id in product_ids if product_id not in completed_ids]
    random.shuffle(available_ids)

    for index, product_id in enumerate(available_ids, start=1):
        if len(completed_ids) >= target_count:
            break

        try:
            detail = fetch_product_detail(session, product_id)
            if detail.get("id"):
                detailed_data.append(detail)
                completed_ids.add(product_id)
            else:
                failed_ids.add(product_id)

        except requests.RequestException as error:
            failed_ids.add(product_id)
            print(f"[WARN] Lỗi tải chi tiết ID {product_id}: {error}")

        if index % 100 == 0:
            print(
                f"Tiến độ: {len(completed_ids)}/{target_count} sản phẩm, "
                f"lỗi: {len(failed_ids)}"
            )
            write_backup(detailed_data)
            save_checkpoint(product_ids, completed_ids, failed_ids)

        time.sleep(random.uniform(0.2, 0.55))

    final_df = pd.DataFrame(detailed_data).drop_duplicates(subset=["id"])
    final_df = final_df.head(target_count)
    final_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    write_backup(final_df.to_dict(orient="records"))
    save_checkpoint(product_ids, set(final_df["id"].tolist()), failed_ids)

    print(f"Hoàn tất: đã lưu {len(final_df)} sản phẩm vào {OUTPUT_FILE}")
    if len(final_df) < target_count:
        print(
            "[INFO] Chưa đủ target trong 1 lần chạy. "
            "Hãy chạy lại script để tiếp tục từ checkpoint."
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Tiki crawler lấy số lượng lớn sản phẩm")
    parser.add_argument("--target", type=int, default=10000, help="Số lượng sản phẩm mục tiêu")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=120,
        help="Số trang tối đa cho mỗi nguồn (category/keyword)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    scrape_tiki_massive(target_count=args.target, max_pages_per_source=args.max_pages)