import time
from scraper.network import fetch_html
from scraper.parser import extract_book_data
from scraper.writer import save_books_to_csv

CATEGORY_NAME = "thieu-nhi"
BASE_URL = f"https://www.fahasa.com/sach-trong-nuoc/{CATEGORY_NAME}.html?order=created_at&limit=24&p="

START_PAGE = 1
END_PAGE =  170 # Chạy thử nghiệm 3 trang trước

def run_scraper():
    print(f"[+] BẮT ĐẦU CÀO DỮ LIỆU DANH MỤC: {CATEGORY_NAME}")
    csv_file_path = f"data/link/{CATEGORY_NAME}_link.csv"
    
    total_scraped = 0
    
    for page in range(START_PAGE, END_PAGE + 1):
        page_url = f"{BASE_URL}{page}"
        print(f"\n[*] --> Đang xử lý Trang {page}/{END_PAGE} | URL: {page_url}")
        
        # Gọi tầng 1: Lấy HTML
        html = fetch_html(page_url)
        if not html:
            print(f"[-] Bỏ qua trang {page} do lỗi tải trang.")
            continue
            
        # Gọi tầng 2: Bóc tách dữ liệu nâng cao
        books = extract_book_data(html)
        print(f"[+] Bóc tách thành công {len(books)} cuốn sách.")
        
        # Gọi tầng 3: Lưu dữ liệu vào file CSV
        save_books_to_csv(books, file_path=csv_file_path)
        print(f"[+] Đã ghi nối tiếp vào file: {csv_file_path}")
        
        total_scraped += len(books)

    print(f"\n[=== HOÀN THÀNH ===] Tổng số sách thu thập được: {total_scraped}")

if __name__ == "__main__":
    start_time = time.time()
    run_scraper()
    print(f"[=== FINISHED ===] Thời gian xử lý: {time.time() - start_time:.2f} giây.")