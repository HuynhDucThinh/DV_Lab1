# Lab 01 — Thu thập & Trực quan hóa Dữ liệu Thương mại Điện tử

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.56-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3D4EAF?style=for-the-badge&logo=plotly&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-ML%20Bonus-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)

> **Báo cáo Lab 01 — Môn Trực quan hóa Dữ liệu (Data Visualization)**
>
> *Khoa Công nghệ Thông tin · Trường Đại học Khoa học Tự nhiên · ĐHQG-HCM · Tháng 4/2026*

---

## Mục lục

- [1. Thông tin nhóm](#1-thông-tin-nhóm)
- [2. Bài toán phân tích](#2-bài-toán-phân-tích)
- [3. Mục tiêu SMART của từng thành viên](#3-mục-tiêu-smart-của-từng-thành-viên)
- [4. Nguồn dữ liệu](#4-nguồn-dữ-liệu)
- [5. Dashboard — Tổng quan các tab](#5-dashboard--tổng-quan-các-tab)
- [6. Cấu trúc dự án](#6-cấu-trúc-dự-án)
- [7. Hướng dẫn cài đặt & chạy](#7-hướng-dẫn-cài-đặt--chạy)
- [8. Công nghệ sử dụng](#8-công-nghệ-sử-dụng)
- [9. Kết quả & Phát hiện chính](#9-kết-quả--phát-hiện-chính)
- [10. Tài liệu tham khảo](#10-tài-liệu-tham-khảo)

---

## 1. Thông tin nhóm

| STT | MSSV | Họ và tên | Vai trò | Đóng góp |
|:---:|:---:|:---|:---|:---:|
| 1 | — | Phạm Ngọc Thanh | Phân tích giá Tiki · Tab Pricing | 20% |
| 2 | — | Cao Tiến Thành | Phân tích giá eBay · Tab Pricing | 20% |
| 3 | — | Lê Hà Thanh Chương | Phân tích xu hướng · Tab Trends | 20% |
| 4 | — | Nguyễn Nhựt Thanh | Phân tích uy tín · Tab Trust | 20% |
| 5 | — | Huỳnh Đức Thịnh | Dashboard architect · Tab Summary · ML Bonus | 20% |

> **Giảng viên hướng dẫn:** *(cập nhật)*
> **Email liên hệ:** huyban.han@gmail.com · vntan.work@gmail.com

---

## 2. Bài toán phân tích

**Phân tích đối chiếu đa nền tảng: Đánh giá tác động của chiến lược định giá, đặc tính sản phẩm và độ uy tín của gian hàng đến hiệu suất tương tác và bán hàng trên hai mô hình thương mại điện tử (Tiki & eBay).**

Dự án thu thập và phân tích dữ liệu từ **Tiki** (nội địa Việt Nam) và **eBay** (quốc tế) thông qua 5 bảng dữ liệu quan hệ chuẩn hóa theo mô hình Star Schema, nhằm làm rõ 3 nhóm vấn đề:

| Nhóm | Câu hỏi nghiên cứu |
|------|-------------------|
| **Định giá & Khuyến mãi** | Phân khúc giá phổ biến nhất? Giảm giá tác động thế nào đến doanh số? |
| **Uy tín & Niềm tin** | Rating ảnh hưởng thế nào đến bán hàng Tiki? Feedback score eBay tác động thế nào đến giá? |
| **Đặc tính & Xu hướng** | Danh mục nào có nguy cơ tồn kho cao? Vòng đời đăng bán eBay như thế nào? |

---

## 3. Mục tiêu SMART của từng thành viên

### Thành viên 1 — Phạm Ngọc Thanh

**Mục tiêu 1:** Phân tích phân bổ giá gốc và giá bán Tiki, xác định các phân khúc giá phổ biến nhất qua chỉ số thống kê mô tả (trung bình, trung vị, IQR), trực quan hóa bằng **Distribution Plot & Box Plot** trên Dashboard.

**Mục tiêu 2:** Đánh giá tác động của Discount Rate và Discount Segment đến sản lượng tiêu thụ và tỷ lệ Best Seller, xây dựng **Stacked Bar Chart có bộ lọc** để xác định mức giảm giá kích thích mua sắm tốt nhất.

---

### Thành viên 2 — Cao Tiến Thành

**Mục tiêu 3:** Phân tích phân phối giá và tổng chi phí cuối cùng của 8 nhóm hàng công nghệ eBay (laptop, smartphone, tablet, camera, monitor, headphones, smartwatch, gaming console), xác định 3 danh mục có giá trung vị cao nhất bằng **Box Plot + Violin Plot**.

**Mục tiêu 4:** Phân tích tác động chính sách phí vận chuyển eBay đến giá cuối, xác định tỷ lệ miễn phí vận chuyển và mức đội giá trung bình, trực quan hóa bằng **Stacked Bar Chart + Scatter Plot**.

---

### Thành viên 3 — Lê Hà Thanh Chương

**Mục tiêu 5:** Phân tích tỷ lệ sản phẩm không có lượt bán/đánh giá trên Tiki, xác định 3 ngành hàng có nguy cơ tồn kho cao nhất, trực quan hóa bằng **Pareto Chart + Risk Bubble Matrix**.

**Mục tiêu 6:** Phân tích phân bổ tình trạng sản phẩm (New/Used/Refurbished) và tác động đến tổng chi phí eBay, xác định phân khúc chiếm thị phần lớn nhất bằng **Treemap + Bar Chart + ECDF**.

---

### Thành viên 4 — Nguyễn Nhựt Thanh

**Mục tiêu 7:** Phân tích tác động của điểm đánh giá trung bình đến doanh số Tiki theo 4 mức (0 / 1–3 / 3–4 / 4–5), so sánh giữa 3 danh mục lớn nhất bằng **Bar Chart + Grouped Bar Chart**.

**Mục tiêu 8:** Phân tích ảnh hưởng của uy tín người bán eBay (4 tầng feedback_score) đến giá niêm yết, đo lường median và IQR từng tầng bằng **Bar Chart + Box Plot phân tầng**.

---

### Thành viên 5 — Huỳnh Đức Thịnh

**Mục tiêu 9:** So sánh phân bổ giá chuẩn hóa nhóm hàng công nghệ Tiki (hàng mới) vs eBay (New/Used/Refurbished) bằng **Overlapping KDE Plot** để đo lường chênh lệch giá trị trung vị và lợi thế phân khúc.

**Mục tiêu 10:** Đánh giá vòng đời đăng bán trung bình của 5 danh mục eBay có số lượng bài đăng cao nhất, xác định ngành hàng luân chuyển nhanh/chậm nhất bằng **Lollipop Chart**.

---

## 4. Nguồn dữ liệu

> ⚠️ Toàn bộ dữ liệu được thu thập bằng **web crawling / REST API trực tiếp** — không sử dụng dataset có sẵn từ Kaggle hay GitHub.

| | **Tiki** | **eBay** |
|:---|:---|:---|
| **Phương pháp** | Tiki REST API (`/api/v2/products`) | eBay Browse API + Web Crawling |
| **Quy mô** | ~10,000 sản phẩm | ~12,000 sản phẩm |
| **Thời gian** | Tháng 4/2026 | Tháng 4/2026 |
| **Danh mục** | Điện tử, Laptop, Sách, Thời trang, Mỹ phẩm... | Electronics, Clothing, Books... |
| **Trường chính** | `price`, `original_price`, `discount_rate`, `rating_average`, `review_count`, `quantity_sold`, `brand`, `category` | `price`, `shipping_cost`, `condition`, `seller_feedback_score`, `category_path` |

### Mô hình dữ liệu (Star Schema)

```
                    ┌─────────────────┐
                    │  dim_product    │
                    │  (product_id,   │
                    │   brand, ...)   │
                    └────────┬────────┘
                             │
┌──────────────────┐         │        ┌──────────────────┐
│  dim_category    │─────────┼─────── │ fact_tiki_        │
│  (category_id,   │         │        │ listings          │
│   category_name) │         │        └──────────────────┘
└──────────────────┘         │
                             │        ┌──────────────────┐
                    ┌────────┴────────┤ fact_ebay_        │
                    │   dim_seller    │ listings          │
                    │  (seller_id,    └──────────────────┘
                    │   feedback...)  │
                    └─────────────────┘
```

---

## 5. Dashboard — Tổng quan các tab

Dashboard được xây dựng bằng **Streamlit** với kiến trúc module hóa, gồm **5 tab phân tích + 1 tab ML bonus**:

### Tab 0 — Overview (Tổng quan)
- Dataset Snapshot: thống kê hình dạng, kiểu dữ liệu, tỷ lệ hoàn chỉnh dữ liệu
- Platform Comparison: so sánh phân phối giá Tiki vs eBay (Box Plot)
- Tiki Price Distribution: histogram giá có kernel density
- Discount Segment Analysis: Stacked Bar doanh số theo phân khúc giảm giá
- eBay Condition Market Share: biểu đồ thị phần tình trạng sản phẩm
- Tiki Stagnation Risk: tỷ lệ sản phẩm không hoạt động

### Tab 1 — Pricing Analysis (Phân tích giá)
- Mục tiêu 1, 2, 3, 4
- Phân tích giá Tiki: phân phối, box plot theo danh mục, Best Seller theo discount segment
- Phân tích giá eBay: violin plot 8 nhóm công nghệ, stacked bar chi phí vận chuyển
- Bộ lọc toàn cục (nền tảng, khoảng giá) tích hợp sidebar

### Tab 2 — Trust & Reputation (Uy tín)
- Mục tiêu 7, 8
- Tiki: grouped bar chart doanh số theo mức rating × danh mục
- eBay: box plot giá theo 4 tầng feedback score người bán
- Scatter plot mối quan hệ rating — review count

### Tab 3 — Characteristics & Trends (Xu hướng)
- Mục tiêu 5, 6, 9, 10
- Tiki Stagnation: Pareto Chart + Risk Bubble Matrix
- eBay Condition: Treemap + Bar Chart + ECDF
- Cross-platform KDE: Overlapping density curves giá công nghệ Tiki vs eBay
- eBay Lollipop: vòng đời đăng bán theo danh mục

### Tab 4 — Machine Learning *(Điểm cộng)*
- **Model:** XGBoost Binary Classifier — dự đoán Best Seller Tiki
- **ROC-AUC:** 0.915 · Accuracy: 83.2% · F1 (BS): 0.706
- Section 1: Model KPI Overview + Classification Report
- Section 2: Confusion Matrix (Plotly heatmap tương tác)
- Section 3: ROC-AUC Curve + SHAP Feature Importance
- Section 4: **Live Predictor** — nhập thông số sản phẩm → dự đoán xác suất Best Seller real-time

### Tab 5 — Executive Summary (Tổng kết)
- Benchmark KPI Tiki vs eBay: so sánh 6 chỉ số chính (bar chart)
- Radar Chart: định vị chiến lược 2 nền tảng trên 5 chiều phân tích
- Key Findings & Recommendations: phát hiện chính + đề xuất actionable

---

## 6. Cấu trúc dự án

```
DV_Lab1/
│
├── data/
│   ├── raw/                            # Dữ liệu thô từ crawling
│   │   ├── products.csv                # ~10,000 sản phẩm Tiki
│   │   └── ebay_products.csv           # ~12,000 sản phẩm eBay
│   └── processed/                      # Star Schema sau tiền xử lý
│       ├── dim_product.csv
│       ├── dim_category.csv
│       ├── dim_seller.csv
│       ├── fact_tiki_listings.csv
│       └── fact_ebay_listings.csv
│
├── models/                             # ML artifacts (pre-trained)
│   ├── xgboost_tiki.pkl                # Model XGBoost đã train
│   ├── encoders.pkl                    # Frequency encoders
│   ├── confusion_matrix.npy            # Ma trận nhầm lẫn (2×2)
│   ├── metrics.json                    # ROC-AUC + classification report
│   ├── roc_auc_curve.png               # ROC curve plot
│   └── shap_summary.png                # SHAP feature importance plot
│
├── notebooks/                          # Jupyter Notebooks
│   ├── 01_data_collection.ipynb
│   ├── 02_data_preprocessing.ipynb
│   └── 03_eda_analysis.ipynb
│
├── src/                                # Python modules tái sử dụng
│   ├── crawlers/
│   │   ├── tiki_crawler.py             # Crawler Tiki (checkpoint + retry)
│   │   └── ebay_crawler.py             # Crawler eBay
│   ├── preprocessing.py                # Impute, clean, feature engineering
│   ├── ml_models.py                    # XGBoost training pipeline
│   └── visualization.py               # Matplotlib/Seaborn helpers
│
├── dashboard/                          # Streamlit Dashboard
│   ├── app.py                          # Entry point
│   ├── config.py                       # Palette, CB mode, constants
│   ├── components/
│   │   ├── header.py                   # Hero banner + CB injection
│   │   ├── sidebar.py                  # Filters + navigation
│   │   ├── navigation.py               # Tab routing + URL state
│   │   ├── footer.py                   # Footer component
│   │   ├── ui_helpers.py               # icon_header, fa_callout
│   │   ├── chart_helpers.py            # KDE, color helpers
│   │   └── kpi_cards.py                # KPI card renderer
│   ├── data/
│   │   ├── loaders.py                  # Cached data loaders
│   │   └── filters.py                  # Filter + clean utilities
│   ├── styles/
│   │   ├── global_css.py               # Dark theme CSS
│   │   └── html_blocks.py              # Hero HTML, KPI header
│   └── tabs/
│       ├── tab0_overview.py            # Tab 0: Overview
│       ├── tab1_pricing.py             # Tab 1: Pricing Analysis
│       ├── tab2_trust.py               # Tab 2: Trust & Reputation
│       ├── tab3_trends.py              # Tab 3: Trends & Characteristics
│       ├── tab4_ml.py                  # Tab 4: Machine Learning (bonus)
│       └── tab5_summary.py             # Tab 5: Executive Summary
│
├── docs/                               # Tài liệu phân tích
│   ├── phan_tich.md                    # Mục tiêu SMART chi tiết
│   ├── data_explained.md               # Giải thích cấu trúc dữ liệu
│   ├── tab0_overview_explained.md
│   ├── tab1_pricing_explained.md
│   ├── tab2_trust_explained.md
│   ├── tab3_trends_explained.md
│   ├── tab4_ml_explained.md            # Giải thích ML model & charts
│   └── yeu_cau.md                      # Yêu cầu đề bài
│
├── reports/
│   └── figures/                        # Biểu đồ xuất từ notebooks
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 7. Hướng dẫn cài đặt & chạy

### Bước 1 — Clone repository

```bash
git clone https://github.com/HuynhDucThinh/DV_Lab1.git
cd DV_Lab1
```

### Bước 2 — Tạo môi trường ảo

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Bước 3 — Cài đặt thư viện

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Bước 4 — Chạy Dashboard

```bash
streamlit run dashboard/app.py
```

Truy cập tại: **http://localhost:8501**

---

### (Tùy chọn) Thu thập dữ liệu lại từ đầu

> Dữ liệu thô đã có sẵn trong `data/raw/`. Chỉ chạy nếu muốn cập nhật mới.

```bash
python src/crawlers/tiki_crawler.py --target 10000
python src/crawlers/ebay_crawler.py
```

### (Tùy chọn) Retrain ML model

```bash
python src/ml_models.py
# Artifacts sẽ được lưu vào models/
```

---

## 8. Công nghệ sử dụng

| Nhóm | Thư viện | Phiên bản |
|:---|:---|:---|
| **Ngôn ngữ** | Python | 3.10+ |
| **Thu thập dữ liệu** | `requests`, `beautifulsoup4`, `selenium`, `playwright` | — |
| **Xử lý dữ liệu** | `pandas`, `numpy` | 2.2.1 / 1.26.4 |
| **Trực quan hóa** | `plotly`, `matplotlib`, `seaborn` | 5.19 / 3.8.3 / 0.13.2 |
| **Dashboard** | `streamlit` | 1.56.0 |
| **Machine Learning** | `xgboost`, `scikit-learn`, `shap`, `joblib` | 3.2 / 1.4 / 0.46 / 1.5 |
| **Utilities** | `tqdm`, `python-dotenv`, `statsmodels` | — |

---

## 9. Kết quả & Phát hiện chính

### Tiki

| Phát hiện | Chi tiết |
|-----------|---------|
| **Phân khúc giá chủ đạo** | 100k–500k VND chiếm tỷ lệ cao nhất |
| **Discount hiệu quả nhất** | Nhóm giảm 30–50% có tỷ lệ Best Seller cao nhất |
| **Rating & Doanh số** | Sản phẩm rating 4–5 có doanh số trung bình cao gấp 2–3× nhóm rating thấp |
| **Stagnation Risk** | ~14.5% sản phẩm không có lượt bán/đánh giá — nguy cơ tồn kho |

### eBay

| Phát hiện | Chi tiết |
|-----------|---------|
| **Chi phí vận chuyển** | ~42% listings có free shipping; phụ phí cao nhất ở nhóm Gaming Console |
| **Condition & Giá** | Hàng "New" cao hơn "Used" trung bình ~35–45% tùy danh mục |
| **Seller Trust** | Top-tier sellers (feedback > 10k) định giá cao hơn ~18% so với low-tier |
| **Listing Lifespan** | Electronics có vòng đời ngắn nhất (~18 ngày), Collectibles dài nhất |

### ML Bonus

| Metric | Kết quả |
|--------|---------|
| **ROC-AUC** | 0.915 (Excellent) |
| **Accuracy** | 83.2% |
| **F1 Best Seller** | 0.706 |
| **Top features** | `rating_average`, `discount_rate`, `Price_Gap` |

---

## 10. Tài liệu tham khảo

1. **Tiki Developer API** — https://api.tiki.vn/
2. **eBay Developer Program** — https://developer.ebay.com/
3. Chen, T. & Guestrin, C. (2016). *XGBoost: A Scalable Tree Boosting System*. KDD 2016.
4. Lundberg, S. & Lee, S. (2017). *A Unified Approach to Interpreting Model Predictions*. NeurIPS 2017.
5. McKinney, W. (2022). *Python for Data Analysis*, 3rd ed. O'Reilly Media.
6. **Streamlit Documentation** — https://docs.streamlit.io/
7. **Plotly Python Documentation** — https://plotly.com/python/

---

<br>
<p align="center">
  <b>E-commerce Analytics Dashboard</b><br>
  <i>Tiki · eBay — Multi-platform Market Intelligence · Apr 2026</i><br>
  <i>Khoa CNTT · Trường ĐH Khoa học Tự nhiên · ĐHQG-HCM</i>
</p>