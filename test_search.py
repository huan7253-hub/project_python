import time
import pandas as pd
from engines.ai_engine import search_by_ai

def main():
    print("[*] Đang nạp cơ sở dữ liệu sách...")
    try:
        df = pd.read_csv("data/books_clean.csv")
    except FileNotFoundError:
        print("[-] Lỗi: Không tìm thấy file data/books_clean.csv. Hãy kiểm tra lại đường dẫn.")
        return

    print("[+] Sẵn sàng! Hệ thống AI đã được tối ưu hóa.")
    print("================================================================")
    print("Mẹo: Hãy thử gõ các câu mô tả nhu cầu ẩn hoặc cảm xúc.")
    print("Ví dụ: 'sách dạy nấu ăn món hoa đơn giản' hoặc 'truyện trinh thám hack não'")
    print("Gõ 'exit' hoặc 'quit' để thoát chương trình.")
    print("================================================================")

    while True:
        query = input("\n[?] Nhập câu hỏi tìm kiếm của bạn: ").strip()
        
        # Điều kiện thoát
        if query.lower() in ['exit', 'quit']:
            print("[*] Đã đóng chương trình test.")
            break
            
        if not query:
            print("[-] Vui lòng nhập nội dung cần tìm.")
            continue

        print("[*] AI đang quét dữ liệu...")
        start_time = time.time()
        match_ids = search_by_ai(query, top_k=5)
        end_time = time.time()
        
        latency = end_time - start_time

        print(f"\n[➔] Kết quả tìm kiếm (Thời gian phản hồi: {latency:.4f} giây):")
        if not match_ids:
            print("[-] Không tìm thấy kết quả phù hợp nào.")
            continue

        print("-" * 60)
        for idx, book_id in enumerate(match_ids, 1):
            # Lọc thông tin từ file CSV
            filtered_df = df[df["id"] == book_id]
            if filtered_df.empty:
                print(f"{idx}. [ID: {book_id}] - Không tìm thấy thông tin chi tiết trong CSV.")
                continue
                
            book_info = filtered_df.iloc[0]
            print(f"{idx}. [ID: {book_id}] - {book_info['title']}")
            print(f"   Tác giả: {book_info['author']} | Giá hiện tại: {book_info['current_price']:,}đ")
            print(f"   Mô tả: {book_info['description'][:150]}...")
            print("-" * 60)

if __name__ == "__main__":
    main()