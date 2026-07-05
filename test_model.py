import os
import time
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

# Cấu hình đường dẫn
CSV_PATH = "data/books_clean.csv"
DB_PATH = "data/chroma_db_test"
COLLECTION_NAME = "fahasa_books_test"
os.environ["HF_TOKEN"] = "token" # Thay bằng token Hugging Face của bạn nếu cần
def run_benchmark():
    print("[*] KHỞI ĐỘNG TIẾN TRÌNH CHẠY THỬ NGHIỆM (BENCHMARK)...")
    
    if not os.path.exists(CSV_PATH):
        print(f"[-] Không tìm thấy file dữ liệu sạch tại: {CSV_PATH}. Hãy chạy merge_clean.py trước.")
        return

    # 1. Đọc thử 100 dòng dữ liệu đầu tiên
    print("[*] Đọc 100 dòng dữ liệu mẫu...")
    df = pd.read_csv(CSV_PATH, nrows=100)
    
    # 2. Tải mô hình AI (Ép chạy trên CPU)
    print("[*] Đang tải mô hình BAAI/bge-m3 vào CPU (Có thể mất 1-2 phút trong lần đầu tiên)...")
    start_load_model = time.time()
    model = SentenceTransformer('BAAI/bge-m3', device='cpu')
    print(f"[+] Tải mô hình thành công trong: {time.time() - start_load_model:.2f} giây.")

    # 3. Khởi tạo ChromaDB lưu trữ cứng xuống đĩa
    chroma_client = chromadb.PersistentClient(path=DB_PATH)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    # 4. Chuẩn bị dữ liệu
    ids = df["id"].astype(str).tolist()
    descriptions = df["description"].astype(str).tolist()

    # 5. Tiến hành đo thời gian sinh Vector (Lõi hiệu năng)
    print("[*] Đang tính toán Vector cho 100 dòng mẫu...")
    start_encode = time.time()
    
    # Chạy encode với batch_size=32 để tối ưu luồng CPU
    embeddings = model.encode(descriptions, batch_size=32, show_progress_bar=True)
    
    end_encode = time.time()
    elapsed_time = end_encode - start_encode
    
    # 6. Đẩy vào ChromaDB
    print("[*] Đang nạp Vector vào ChromaDB Test...")
    collection.add(
        embeddings=embeddings.tolist(),
        ids=ids
    )
    
    # 7. Tính toán và dự báo chỉ số hiệu năng
    avg_speed = 100 / elapsed_time
    estimated_full_time_mins = (32000 / avg_speed) / 60
    
    print("\n[=== KẾT QUẢ ĐO ĐẠC HIỆU NĂNG ===]")
    print(f"-> Thời gian xử lý 100 dòng: {elapsed_time:.2f} giây.")
    print(f"-> Tốc độ xử lý trung bình trên CPU: {avg_speed:.2f} dòng/giây.")
    print(f"-> ĐƯỜNG BẢN ĐỒ DỰ BÁO: Với 32k dòng, máy của bạn sẽ mất khoảng: {estimated_full_time_mins:.2f} phút.")
    print(f"-> Thư mục DB test đã lưu tại: {DB_PATH}")
    print("[+] Tiến trình test hoàn tất an toàn. Hãy kiểm tra xem ổ đĩa có sinh thư mục không.")

if __name__ == "__main__":
    run_benchmark()