import os
import glob
import pandas as pd

# Cấu hình đường dẫn quét các file sạch từ danh mục
INPUT_PATTERN = "../data/clean/*_clean.csv" 
OUTPUT_FILE = "../data/books_clean.csv"

def main():
    # 1. Thu thập toàn bộ file danh mục đã làm sạch sơ bộ
    file_list = glob.glob(INPUT_PATTERN)
    if not file_list:
        print(f"[-] Không tìm thấy file dữ liệu sạch nào tại: {INPUT_PATTERN}")
        return

    print(f"[*] Tìm thấy {len(file_list)} file danh mục. Tiến hành gộp dữ liệu...")
    
    # Đọc và gộp thành một DataFrame duy nhất
    df_list = [pd.read_csv(f) for f in file_list]
    df = pd.concat(df_list, ignore_index=True)
    
    # 2. Khử trùng lặp tuyệt đối theo URL sách
    initial_rows = len(df)
    df.drop_duplicates(subset=["link"], inplace=True)
    print(f"[+] Đã loại bỏ {initial_rows - len(df)} dòng dữ liệu trùng lặp.")

    # 3. Loại bỏ hoàn toàn các cột thừa/gây nhiễu hệ thống
    columns_to_drop = ["text_for_ai", "weight_gr"]
    df.drop(columns=columns_to_drop, errors="ignore", inplace=True)

    # 4. Ép chết kiểu dữ liệu số và xử lý dữ liệu khuyết (Chống sập MySQL)
    df["publish_year"] = pd.to_numeric(df["publish_year"], errors="coerce").fillna(0).astype(int)
    df["page_count"] = pd.to_numeric(df["page_count"], errors="coerce").fillna(0).astype(int)
    df["current_price"] = pd.to_numeric(df["current_price"], errors="coerce").fillna(0).astype(int)
    df["old_price"] = pd.to_numeric(df["old_price"], errors="coerce").fillna(0).astype(int)

    # 5. Chuẩn hóa dữ liệu chuỗi văn bản
    df["author"] = df["author"].fillna("Đang cập nhật").astype(str).str.strip()
    df["publisher"] = df["publisher"].fillna("Đang cập nhật").astype(str).str.strip()
    df["description"] = df["description"].fillna("").astype(str).str.strip()
    
    # Loại bỏ những cuốn hoàn toàn không có mô tả vì AI không thể học text rỗng
    initial_valid = len(df)
    df = df[df["description"] != ""]
    print(f"[+] Đã lọc bỏ {initial_valid - len(df)} cuốn không có phần mô tả (description).")

    # 6. Chủ động sinh cột ID số nguyên duy nhất đặt ở đầu bảng
    df.insert(0, "id", range(1, len(df) + 1))

    # 7. Xuất file đóng gói cuối cùng để phân phối cho nhóm
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    
    print(f"\n[=== HOÀN THÀNH ===]")
    print(f"-> File sạch tổng hợp đã được lưu tại: {OUTPUT_FILE}")
    print(f"-> Quy mô kho dữ liệu: {len(df)} cuốn sách sạch cấu trúc.")

if __name__ == "__main__":
    main()