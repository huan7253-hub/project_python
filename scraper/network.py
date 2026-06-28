import time
import random
import requests

# Danh sách các User-Agent phổ biến để giả lập các trình duyệt khác nhau
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
]

def fetch_html(url, retries=3, backoff_factor=2):
    """
    Hàm chuyên trách việc tải HTML từ URL.
    Có tích hợp giả lập trình duyệt, delay ngẫu nhiên và tự động thử lại (retry) nếu lỗi.
    """
    # 1. Cơ chế ẩn mình: Chọn ngẫu nhiên một User-Agent
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    }
    
    # 2. Cơ chế an toàn: Vòng lặp thử lại nếu gặp lỗi mạng (500, 502, 504...)
    for attempt in range(retries):
        try:
            # Gửi request với thời gian timeout là 10 giây (tránh treo script)
            response = requests.get(url, headers=headers, timeout=10)
            
            # Nếu HTTP Status Code là 200 (Thành công), trả về HTML luôn
            if response.status_code == 200:
                # 3. Cơ chế hạ nhiệt (Rate Limiting): Nghỉ ngẫu nhiên 1 đến 3 giây trước khi thoát hàm
                time.sleep(random.uniform(1.0, 3.0))
                return response.text
                
            print(code_error := f"[!] Lỗi HTTP {response.status_code} khi truy cập: {url}")
            
        except requests.RequestException as e:
            print(f"[!] Lỗi kết nối ở lượt thử {attempt + 1}/{retries}: {e}")
            
        # Nếu bị lỗi, đợi một khoảng thời gian tăng dần (Exponential Backoff) rồi thử lại
        if attempt < retries - 1:
            sleep_time = backoff_factor ** attempt
            print(f"[*] Thử lại sau {sleep_time} giây...")
            time.sleep(sleep_time)
            
    # Nếu thử hết số lần quy định mà vẫn thất bại, trả về None
    return None