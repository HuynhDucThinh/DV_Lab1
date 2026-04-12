# Lab 01: Thu thập & Trực quan hóa dữ liệu thương mại điện tử

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?style=for-the-badge&logo=jupyter&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow?style=for-the-badge)

> **Báo cáo Lab 01 — Môn Trực quan hóa dữ liệu (Data Visualization)**
>
> *Khoa Công nghệ Thông tin, Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM*

---

## Mục lục

- [1. Thông tin nhóm](#1-thông-tin-nhóm)
- [2. Bài toán phân tích chung](#2-bài-toán-phân-tích-chung)
- [3. Mục tiêu phân tích của từng thành viên](#3-mục-tiêu-phân-tích-của-từng-thành-viên)
- [4. Nguồn dữ liệu](#4-nguồn-dữ-liệu)
- [5. Cấu trúc dự án](#5-cấu-trúc-dự-án)
- [6. Hướng dẫn cài đặt & sử dụng](#6-hướng-dẫn-cài-đặt--sử-dụng)
- [7. Công nghệ sử dụng](#7-công-nghệ-sử-dụng)
- [8. Kết quả chính](#8-kết-quả-chính)
- [9. Tài liệu tham khảo](#9-tài-liệu-tham-khảo)

---

## 1. Thông tin nhóm

| STT | MSSV | Họ và tên | Vai trò | Tỷ lệ đóng góp |
| :---: | :---: | :--- | :--- | :---: |
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

> **Giảng viên hướng dẫn:** ...
> **Email liên hệ:** huyban.han@gmail.com · vntan.work@gmail.com

---

## 2. Bài toán phân tích chung

**Phân tích xu hướng bán hàng và hành vi định giá trên sàn thương mại điện tử đa quốc gia (Tiki & eBay)**

Dự án thu thập và phân tích dữ liệu sản phẩm từ hai sàn thương mại điện tử: **Tiki** (Việt Nam) và **eBay** (quốc tế), nhằm trả lời các câu hỏi nghiệp vụ như:

- Các danh mục sản phẩm nào có mức giá và tỷ lệ chiết khấu cao nhất?
- Mối quan hệ giữa đánh giá của người dùng, số lượng bán và chiến lược định giá là gì?
- Sự khác biệt về hành vi định giá giữa thị trường trong nước (Tiki) và quốc tế (eBay) như thế nào?

---

## 3. Mục tiêu phân tích của từng thành viên

### Thành viên 1: [Tên]

**Mục tiêu 1:**
- **S** (Specific):
- **M** (Measurable):
- **A** (Achievable):
- **R** (Relevant):
- **T** (Time-bound):

**Mục tiêu 2:**
- **S** (Specific):
- **M** (Measurable):
- **A** (Achievable):
- **R** (Relevant):
- **T** (Time-bound):

### Thành viên 2: [Tên]

**Mục tiêu 1:**
- **S** (Specific):
- **M** (Measurable):
- **A** (Achievable):
- **R** (Relevant):
- **T** (Time-bound):

**Mục tiêu 2:**
- **S** (Specific):
- **M** (Measurable):
- **A** (Achievable):
- **R** (Relevant):
- **T** (Time-bound):

### Thành viên 3: [Tên]

*[Tương tự — 2 mục tiêu SMART]*

### Thành viên 4: [Tên]

*[Tương tự — 2 mục tiêu SMART]*

### Thành viên 5: [Tên]

*[Tương tự — 2 mục tiêu SMART]*

---

## 4. Nguồn dữ liệu

> ⚠️ **Lưu ý:** Toàn bộ dữ liệu được thu thập bằng **web crawling / API trực tiếp** — không sử dụng dataset có sẵn từ Kaggle hay GitHub theo yêu cầu đề bài.

| | **Tiki** | **eBay** |
| :--- | :--- | :--- |
| **Phương pháp** | Tiki REST API (`/api/v2/products`) | eBay Browse API / Web Crawling |
| **Quy mô** | ~10,000 sản phẩm | ~12,000 sản phẩm |
| **Thời gian thu thập** | Tháng 4/2026 | Tháng 4/2026 |
| **File thô** | `data/raw/products.csv` | `data/raw/ebay_products.csv` |
| **Danh mục thu thập** | Điện thoại, Laptop, Sách, Thời trang, Mỹ phẩm, ... | Electronics, Clothing, Books, ... |
| **Các trường chính** | `id`, `name`, `price`, `original_price`, `discount_rate`, `rating_average`, `review_count`, `quantity_sold`, `brand`, `category` | `item_id`, `title`, `price`, `shipping_cost`, `condition`, `seller_username`, `seller_feedback_score`, `category_path`, ... |

### Mô hình dữ liệu sau tiền xử lý (Star Schema)

```
fact_tiki_listings.csv      ──►  dim_product.csv
fact_ebay_listings.csv      ──►  dim_category.csv
                            ──►  dim_seller.csv
```

---

## 5. Cấu trúc dự án

```text
DV_Lab1/
│
├── data/
│   ├── raw/                            # Dữ liệu thô từ crawling
│   │   ├── products.csv                # ~10,000 sản phẩm Tiki
│   │   └── ebay_products.csv           # ~12,000 sản phẩm eBay
│   └── processed/                      # Dữ liệu đã xử lý (Star Schema)
│       ├── dim_product.csv
│       ├── dim_category.csv
│       ├── dim_seller.csv
│       ├── fact_tiki_listings.csv
│       └── fact_ebay_listings.csv
│
├── notebooks/                          # Jupyter Notebooks (chạy theo thứ tự)
│   ├── 01_data_collection.ipynb        # Thu thập & kiểm tra dữ liệu thô
│   ├── 02_data_preprocessing.ipynb     # Tiền xử lý, xử lý ngoại lệ, feature engineering
│   └── 03_eda_analysis.ipynb           # Phân tích khám phá & trực quan hóa
│
├── src/                                # Module Python tái sử dụng
│   ├── __init__.py
│   ├── crawlers/
│   │   ├── tiki_crawler.py             # Crawler Tiki (checkpoint, retry, ~279 dòng)
│   │   └── ebay_crawler.py             # Crawler eBay
│   ├── preprocessing.py                # Xử lý missing values, outliers, feature engineering
│   └── visualization.py               # Hàm vẽ biểu đồ tái sử dụng
│
├── dashboard/                          # Interactive Dashboard
│   └── app.py                          # Streamlit app (≥ 3 tabs)
│
├── reports/
│   └── figures/                        # Biểu đồ xuất từ notebooks
│
├── requirements.txt                    # Thư viện Python cần thiết
├── .gitignore
└── README.md                           # File này
```

---

## 6. Hướng dẫn cài đặt & sử dụng

### Bước 1 — Clone repository

```bash
git clone [URL_REPOSITORY]
cd DV_Lab1
```

### Bước 2 — Tạo môi trường ảo

*Dùng `venv` (khuyến nghị cho VS Code):*

```bash
python -m venv venv

# Kích hoạt trên Windows:
venv\Scripts\activate

# Kích hoạt trên macOS/Linux:
source venv/bin/activate
```

### Bước 3 — Cài đặt thư viện

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Bước 4 — Thu thập dữ liệu (nếu chạy lại từ đầu)

```bash
# Thu thập dữ liệu Tiki (mặc định 10,000 sản phẩm)
python src/crawlers/tiki_crawler.py --target 10000

# Thu thập dữ liệu eBay
python src/crawlers/ebay_crawler.py
```

> **Lưu ý:** Dữ liệu thô đã được thu thập sẵn trong `data/raw/`. Bước này chỉ cần chạy nếu muốn cập nhật dữ liệu mới.

### Bước 5 — Chạy Notebooks theo thứ tự

```bash
jupyter notebook
```

Mở và chạy lần lượt:
1. `notebooks/01_data_collection.ipynb`
2. `notebooks/02_data_preprocessing.ipynb` → tạo ra các file trong `data/processed/`
3. `notebooks/03_eda_analysis.ipynb` → xuất biểu đồ vào `reports/figures/`

### Bước 6 — Chạy Interactive Dashboard

```bash
streamlit run dashboard/app.py
```

Truy cập dashboard tại: `http://localhost:8501`

---

## 7. Công nghệ sử dụng

| Nhóm | Thư viện |
| :--- | :--- |
| **Ngôn ngữ** | Python 3.10+ |
| **Thu thập dữ liệu** | `requests`, `urllib3`, `selenium`, `playwright` |
| **Xử lý dữ liệu** | `pandas`, `numpy` |
| **Trực quan hóa** | `matplotlib`, `seaborn`, `plotly`, `altair` |
| **Dashboard** | `streamlit` / `dash` |
| **Machine Learning** *(bonus)* | `scikit-learn`, `xgboost`, `lightgbm` |
| **Tiện ích** | `tqdm`, `python-dotenv` |

---

## 8. Kết quả chính

*[Cập nhật sau khi hoàn thành phân tích — tóm tắt các phát hiện quan trọng từ EDA và dashboard]*

---

## 9. Tài liệu tham khảo

1. Tiki Developer API — https://api.tiki.vn/
2. eBay Developer Program — https://developer.ebay.com/
3. McKinney, W. (2022). *Python for Data Analysis*, 3rd ed. O'Reilly Media.
4. *Streamlit Documentation* — https://docs.streamlit.io/

---

<br>
<p align="center">
  <i>Built with ❤️ | Khoa CNTT, Trường ĐH Khoa học Tự nhiên, ĐHQG-HCM | 2026</i>
</p>