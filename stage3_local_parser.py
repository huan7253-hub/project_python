import os
import json
import csv
from bs4 import BeautifulSoup

CATEGORY_NAME = 'am-nhac-my-thuat-thoi-trang'
RAW_JSONL_PATH = f"data/raw/{CATEGORY_NAME}_raw.jsonl"
OUTPUT_CLEAN_CSV = f"data/clean/{CATEGORY_NAME}_clean.csv"

def clean_text(text):
    """Làm sạch khoảng trắng thừa, dấu tab, dấu xuống dòng trong văn bản thô"""
    if not text:
        return ""
    return " ".join(text.strip().split())

def parse_single_record(line_str):
    """Phân tích cú pháp một dòng HTML thô sang dictionary dữ liệu sạch"""
    try:
        raw_data = json.loads(line_str)
    except json.JSONDecodeError:
        return None

    # Khởi tạo bản thiết kế dữ liệu đầu ra
    clean_data = {
        "link": raw_data.get("link", ""),
        "title": "Đang cập nhật",
        "category_path": "",
        "author": "Đang cập nhật",
        "publisher": "Đang cập nhật",
        "publish_year": "Đang cập nhật",
        "weight_gr": 0,
        "page_count": 0,
        "current_price": 0,
        "old_price": 0,
        "description": ""
    }

    # 1. Bóc tách Breadcrumb (Thể loại phân cấp)
    if "breadcrumb_raw" in raw_data and raw_data["breadcrumb_raw"]:
        soup_bread = BeautifulSoup(raw_data["breadcrumb_raw"], "html.parser")
        bread_items = [li.text.strip() for li in soup_bread.find_all("li") if li.text.strip()]
        clean_data["category_path"] = " | ".join(bread_items)

    # 2. Bóc tách khối Chi tiết (Tên, Giá, Thuộc tính vật lý)
    if "detail_raw" in raw_data and raw_data["detail_raw"]:
        soup_detail = BeautifulSoup(raw_data["detail_raw"], "html.parser")
        
        # 2.1 Lấy Tên sách
        title_tag = soup_detail.find("h1", class_="fhs_name_product_desktop")
        if title_tag:
            clean_data["title"] = clean_text(title_tag.text)
            
        # 2.2 Lấy Giá bán hiện tại
        special_price_tag = soup_detail.find("p", class_="special-price")
        if special_price_tag:
            price_span = special_price_tag.find("span", class_="price")
            if price_span:
                price_text = price_span.text.replace("đ", "").replace(".", "").strip()
                clean_data["current_price"] = int(price_text) if price_text.isdigit() else 0
                
        # 2.3 Lấy Giá bìa (Giá cũ)
        old_price_tag = soup_detail.find("p", class_="old-price")
        if old_price_tag:
            old_price_span = old_price_tag.find("span", class_="price")
            if old_price_span:
                old_price_text = old_price_span.text.replace("đ", "").replace(".", "").strip()
                clean_data["old_price"] = int(old_price_text) if old_price_text.isdigit() else 0

        # 2.4 Quét bảng thông tin chi tiết bằng cơ chế Key-Value linh hoạt
        # Cách này giúp lấy dữ liệu chuẩn xác bất kể các hàng bị tráo đổi thứ tự
        table_rows = soup_detail.find_all("tr")
        for row in table_rows:
            label_tag = row.find(class_="table-label")
            val_tag = row.find("td")
            if label_tag and val_tag:
                label = clean_text(label_tag.text)
                value = clean_text(val_tag.text)
                
                if "Tác giả" in label:
                    clean_data["author"] = value
                elif "NXB" in label:
                    clean_data["publisher"] = value
                elif "Năm XB" in label:
                    clean_data["publish_year"] = value
                elif "Trọng lượng" in label:
                    # Trích xuất và đưa về kiểu số nguyên cho trọng lượng
                    clean_data["weight_gr"] = int(value) if value.isdigit() else 0
                elif "Số trang" in label:
                    # Trích xuất và đưa về kiểu số nguyên cho số trang
                    clean_data["page_count"] = int(value) if value.isdigit() else 0

        # 2.5 Lấy phần Mô tả sản phẩm (Nằm trong khối detail_raw)
        desc_tag = soup_detail.find(id="desc_content")
        if desc_tag:
            clean_data["description"] = clean_text(desc_tag.text)

    return clean_data

def main():
    print("[*] Bắt đầu bóc tách và chuẩn hóa dữ liệu sang CSV...")
    if not os.path.exists(RAW_JSONL_PATH):
        print(f"[-] Không tìm thấy file dữ liệu thô: {RAW_JSONL_PATH}")
        return

    # Danh sách các cột tiêu đề của file CSV đầu ra
    headers = [
        "link", "title", "category_path", "author", "publisher", 
        "publish_year", "weight_gr", "page_count", "current_price", 
        "old_price", "description"
    ]

    os.makedirs(os.path.dirname(OUTPUT_CLEAN_CSV), exist_ok=True)
    
    success_count = 0
    
    # Đọc ghi theo cơ chế Streaming (Từng dòng một) để bảo vệ RAM
    with open(RAW_JSONL_PATH, "r", encoding="utf-8") as infile, \
         open(OUTPUT_CLEAN_CSV, "w", newline="", encoding="utf-8") as outfile:
         
        writer = csv.DictWriter(outfile, fieldnames=headers)
        writer.writeheader()
        
        for line in infile:
            parsed_data = parse_single_record(line)
            if parsed_data:
                writer.writerow(parsed_data)
                success_count += 1

    print(f"[=== HOÀN THÀNH ===] Đã xử lý và xuất thành công {success_count} cuốn sách ra file: {OUTPUT_CLEAN_CSV}")

if __name__ == "__main__":
    main()