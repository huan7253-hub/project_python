import os
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from scraper.network import fetch_html
from bs4 import BeautifulSoup
import csv

# Cấu hình đường dẫn file
CATEGORY_NAME = 'kinh-te-chinh-tri-phap-ly'
INPUT_CSV = f"../data/link/{CATEGORY_NAME}_link.csv"
OUTPUT_JSONL = f"../data/raw/{CATEGORY_NAME}_raw.jsonl"
MAX_THREADS = 7

# Khởi tạo Lock để tránh xung đột khi nhiều luồng cùng ghi vào một file JSONL một lúc
file_lock = Lock()

def load_target_links(csv_path):
    """Đọc file CSV bằng thư viện chuyên dụng để tránh lỗi dấu phẩy trong tên sách"""
    links = []
    if not os.path.exists(csv_path):
        print(f"[-] Không tìm thấy file đầu vào: {csv_path}")
        return links
        
    with open(csv_path, "r", encoding="utf-8") as f:
        # Sử dụng csv.reader thay vì split(",") thủ công
        reader = csv.reader(f)
        # Bỏ qua dòng header
        next(reader, None)
        
        for row in reader:
            # row là một list các cột, row[1] sẽ luôn là cột Link chuẩn xác 100%
            if len(row) > 1:
                links.append(row[1])
    return links

def load_scraped_links(jsonl_path):
    """Đọc file JSONL hiện tại để biết những link nào đã cào rồi (Checkpoint)"""
    scraped_links = set()
    if os.path.exists(jsonl_path):
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if "link" in data:
                        scraped_links.add(data["link"])
                except json.JSONDecodeError:
                    continue
    return scraped_links

def extract_raw_snippets(html_content):
    """Nhận HTML thô của trang chi tiết, cắt lấy 3 khối quan trọng nhất"""
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Tìm 3 khối theo cấu trúc bạn đã khảo sát
    breadcrumb_tags = soup.find_all(class_="breadcrumb")
    breadcrumb_html = str(breadcrumb_tags[0]) if breadcrumb_tags else ""
    
    detail_tag = soup.find(class_="product-essential-detail-parent")
    detail_html = str(detail_tag) if detail_tag else ""
    
    review_tag = soup.find(id="product_view_review")
    review_html = str(review_tag) if review_tag else ""
    
    # Nếu cả 3 khối đều trống rỗng, có thể trang bị lỗi hoặc cấu trúc thay đổi
    if not breadcrumb_html and not detail_html and not review_html:
        return None
        
    return {
        "breadcrumb_raw": breadcrumb_html.strip(),
        "detail_raw": detail_html.strip(),
        "review_raw": review_html.strip()
    }

def crawl_single_link(link, index, total):
    """Hàm xử lý cho cụ thể một luồng (Thread)"""
    # Gửi request lấy HTML (Hàm fetch_html gốc của mình đã có sẵn delay ngẫu nhiên)
    html = fetch_html(link)
    
    if not html:
        return {"status": "fail", "link": link, "msg": "Lỗi kết nối mạng"}
        
    snippets = extract_raw_snippets(html)
    if not snippets:
        return {"status": "fail", "link": link, "msg": "Không tìm thấy thẻ cấu trúc"}
        
    snippets["link"] = link
    
    # Dùng Thread Lock để đảm bảo tại một thời điểm chỉ có 1 luồng được quyền ghi file
    # Tránh việc dữ liệu của các luồng bị ghi đè hoặc chèn lẫn lộn vào nhau gây lỗi file JSONL
    with file_lock:
        with open(OUTPUT_JSONL, "a", encoding="utf-8") as f:
            f.write(json.dumps(snippets, ensure_ascii=False) + "\n")
            
    return {"status": "success", "link": link}

def main():
    print("[*] Khởi động Giai đoạn 2 bằng ĐA LUỒNG (Multi-threading)...")
    
    all_links = load_target_links(INPUT_CSV)
    scraped_links = load_scraped_links(OUTPUT_JSONL)
    links_to_crawl = [link for link in all_links if link not in scraped_links]
    
    total_todo = len(links_to_crawl)
    print(f"[+] Tổng số link: {len(all_links)} | Đã cào: {len(scraped_links)} | Cần cào tiếp: {total_todo}")
    
    if total_todo == 0:
        print("[+] Đã hoàn thành cào toàn bộ!")
        return

    os.makedirs(os.path.dirname(OUTPUT_JSONL), exist_ok=True)
    
    # Khởi tạo Executor quản lý đa luồng
    print(f"[*] Đang kích hoạt {MAX_THREADS} luồng chạy song song...")
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Nạp tất cả các tác vụ cào vào hàng đợi của Executor
        futures = {
            executor.submit(crawl_single_link, link, idx, total_todo): link 
            for idx, link in enumerate(links_to_crawl, 1)
        }
        
        # Lắng nghe kết quả trả về từ các luồng khi chúng hoàn thành (Không theo thứ tự gửi)
        for idx, future in enumerate(as_completed(futures), 1):
            result = future.result()
            link = futures[future]
            
            if result["status"] == "success":
                success_count += 1
                print(f"[+] [{idx}/{total_todo}] Thành công -> {link}")
            else:
                print(f"[-] [{idx}/{total_todo}] Thất bại ({result['msg']}) -> {link}")

    print(f"\n[=== HOÀN THÀNH BATCH ===] Đã cào thêm được: {success_count} cuốn.")

if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"[=== FINISHED ===] Thời gian xử lý: {time.time() - start_time:.2f} giây.")