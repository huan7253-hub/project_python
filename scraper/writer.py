import os
import csv

def save_books_to_csv(books_data, file_path="data/raw_books.csv"):
    """
    Hàm lưu danh sách dictionary dữ liệu sách vào file CSV.
    Hỗ trợ ghi nối tiếp (append) và tự động tạo tiêu đề cột (header) nếu là file mới.
    """
    if not books_data:
        return
        
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    # Xác định các tiêu đề cột dựa trên các key của dictionary
    headers = ["title", "link", "current_price", "old_price", "discount", "rating"]
    
    # Kiểm tra xem file đã tồn tại chưa để quyết định có viết dòng Header không
    file_exists = os.path.exists(file_path)
    
    # Mở file ở chế độ 'a' (append) và thiết lập newline='' để không bị dòng trống thừa trong CSV
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        
        # Nếu file mới tinh, viết dòng tiêu đề cột trước
        if not file_exists:
            writer.writeheader()
            
        # Viết toàn bộ các dòng dữ liệu sách thu được
        writer.writerows(books_data)