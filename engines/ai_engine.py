import os
import torch
import chromadb
from sentence_transformers import SentenceTransformer

# Ép số luồng CPU tối ưu để không bị nghẽn cổ chai hệ thống
torch.set_num_threads(4)

# Khởi tạo Client kết nối trực tiếp vào thư mục DB đã giải nén từ Colab
DB_PATH = os.path.join("data", "chroma_db")
CHROMA_CLIENT = chromadb.PersistentClient(path=DB_PATH)
COLLECTION = CHROMA_CLIENT.get_collection(name="fahasa_books")

# Biến toàn cục giữ mô hình trên RAM
_MODEL_INSTANCE = None

def get_ai_model():
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        print("[*] Lần đầu khởi tạo: Đang nạp mô hình bge-m3 lên RAM...")
        _MODEL_INSTANCE = SentenceTransformer('BAAI/bge-m3', device='cpu')
        _MODEL_INSTANCE.max_seq_length = 512  # Giới hạn token tối ưu tốc độ CPU
    return _MODEL_INSTANCE

def search_by_ai(query, top_k=10):
    """
    Hàm lõi tìm kiếm ngữ nghĩa.
    Đầu vào: Chuỗi câu hỏi tự nhiên.
    Đầu ra: List các ID dạng số nguyên đã sắp xếp.
    """
    if not query.strip():
        return []
        
    model = get_ai_model()
    
    # 1. Vector hóa câu hỏi trên CPU (Rất nhanh nhờ giới hạn 512 tokens)
    query_vector = model.encode(query, show_progress_bar=False).tolist()
    
    # 2. Quét không gian vector trên ChromaDB
    results = COLLECTION.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )
    
    # 3. Ép kiểu ID chuỗi từ ChromaDB về INT để khớp MySQL
    raw_ids = results['ids'][0]
    int_ids = [int(x) for x in raw_ids]
    
    return int_ids