# Lab 01: Thu thập dữ liệu và Trực quan hóa dữ liệu bằng Python

## Thông tin nhóm
| STT | MSSV | Họ và tên | Tỷ lệ đóng góp |
|-----|------|-----------|----------------|
| 1   |      |           |                |
| 2   |      |           |                |
| 3   |      |           |                |
| 4   |      |           |                |
| 5   |      |           |                |

## Bài toán phân tích chung
*[Mô tả bài toán phân tích chung của nhóm - ví dụ: Phân tích xu hướng bán hàng trên sàn thương mại điện tử]*

## Mục tiêu phân tích của từng thành viên

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
*[Tương tự như trên]*

## Cấu trúc dự án
```
DV_Lab1/
├── data/                      # Thư mục chứa dữ liệu
│   ├── raw/                   # Dữ liệu thô từ crawling
│   └── processed/             # Dữ liệu đã xử lý
├── notebooks/                 # Jupyter notebooks
│   ├── 01_data_collection.ipynb
│   ├── 02_data_preprocessing.ipynb
│   └── 03_eda_analysis.ipynb
├── src/                       # Source code
│   ├── crawlers/              # Code thu thập dữ liệu
│   ├── preprocessing/         # Code tiền xử lý
│   └── visualization/         # Code trực quan hóa
├── dashboard/                 # Interactive Dashboard
│   └── app.py                 # Streamlit/Dash app
├── reports/                   # Báo cáo và hình ảnh
│   └── figures/               # Biểu đồ xuất ra
├── requirements.txt           # Thư viện Python cần thiết
└── README.md                  # File này
```

## Hướng dẫn cài đặt

### 1. Clone repository
```bash
git clone [URL_REPOSITORY]
cd DV_Lab1
```

### 2. Tạo môi trường ảo (khuyến nghị)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

## Hướng dẫn sử dụng

### Thu thập dữ liệu
```bash
# Chạy crawler
python src/crawlers/shopee_crawler.py
```

### Chạy Dashboard
```bash
# Streamlit
streamlit run dashboard/app.py

# Hoặc Dash
python dashboard/app.py
```

## Nguồn dữ liệu
- **Sàn thương mại điện tử:** [Tên sàn]
- **Phương pháp thu thập:** Web Crawling / API
- **Thời gian thu thập:** [Ngày bắt đầu] - [Ngày kết thúc]
- **Quy mô dữ liệu:** [Số lượng] dòng

## Công nghệ sử dụng
- **Ngôn ngữ:** Python 3.x
- **Thu thập dữ liệu:** requests, BeautifulSoup4, Selenium
- **Xử lý dữ liệu:** pandas, numpy
- **Trực quan hóa:** matplotlib, seaborn, plotly
- **Dashboard:** streamlit / dash
- **Machine Learning (nếu có):** scikit-learn

## Kết quả chính
*[Tóm tắt các phát hiện quan trọng từ phân tích]*

## Tài liệu tham khảo
1. [Nguồn 1]
2. [Nguồn 2]

## Liên hệ
- Email giảng viên: huyban.han@gmail.com, vntan.work@gmail.com
