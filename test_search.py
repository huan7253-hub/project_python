from sentence_transformers import SentenceTransformer
import chromadb

# 1. Kết nối database đã lưu ở ổ cứng
chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_collection(name="fahasa_books")

# 2. Nạp lại mô hình AI
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# 3. Gõ câu hỏi bất kỳ bằng ngôn ngữ tự nhiên vào đây để test
query = "tìm sách của Thomas L Friedman"

# 4. Vector hóa câu hỏi và quét không gian toán học
query_vector = model.encode(query).tolist()
results = collection.query(
    query_embeddings=[query_vector],
    n_results=3 # Bốc ra top 3 cuốn tương đồng nhất
)

# 5. In kết quả ra màn hình
print(f"=== KẾT QUẢ TÌM KIẾM CHO: '{query}' ===")
for i in range(len(results['ids'][0])):
    meta = results['metadatas'][0][i]
    print(f"\nTop {i+1}: {meta['title']}")
    print(f"-> Tác giả: {meta['author']} | Thể loại: {meta['category_path']}")
    print(f"-> Giá bán: {meta['current_price']}đ")