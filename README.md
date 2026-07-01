# 📖 HƯỚNG DẪN THU THẬP VÀ TRÍCH XUẤT DỮ LIỆU SÁCH FAHASA

Tài liệu này hướng dẫn các thành viên trong nhóm thiết lập môi trường và chạy script cào dữ liệu chi tiết theo từng hạng mục được phân công.

---

## 🛠️ Bước 1: Thiết lập môi trường làm việc

1. **Tải và Giải nén:** Tải file ZIP từ GitHub của nhóm về máy tính và giải nén.
2. **Mở Dự án:** Khởi động **VS Code**, chọn `Open Folder` và tìm đến thư mục vừa giải nén.
3. **Thêm dữ liệu đầu vào:** Tải thư mục `data` (được gửi riêng qua Zalo) và bỏ vào thư mục gốc của dự án.
4. **Cài đặt Thư viện:** Mở Terminal trong VS Code (có thể bật môi trường ảo venv hoặc cài trực tiếp trên máy) và chạy lệnh sau để cài đặt các thư viện bắt buộc:
   ```bash
   pip install requests beautifulsoup4
## Bước 2: Cào dữ liệu chi tiết (Giai đoạn 2)
1. Mở file txt đính kèm trong dự án để xem danh sách các danh mục (Hạng mục sách).
2. Mở file stage2_crawl_raw.py và cấu hình lại các thông số ở đầu file:
- Tìm biến CATEGORY_NAME và thay thế bằng tên danh mục bạn được phân công.
- Có thể tùy chỉnh số luồng chạy song song tại biến MAX_THREADS (Khuyến nghị: Giữ từ 5 đến 8).
3. Chạy file: Bấm nút Run file Python trên VS Code.
4. Kiểm tra đầu ra: Vào thư mục data/ xem hệ thống đã tự tạo ra file thô .jsonl tương ứng với danh mục đó chưa

## Bước 3: Trích xuất và Làm sạch dữ liệu Offline (Giai đoạn 3)
Sau khi file thô ở Bước 2 đã chạy xong hoàn toàn (hoặc khi muốn kiểm tra thử dữ liệu sạch):
1. Mở file stage3_local_parser.py.
2. Tìm biến CATEGORY_NAME và thay đổi bằng chính xác tên danh mục bạn vừa cào xong ở Bước 2.
3. Chạy file: Bấm Run để script xử lý bóc tách offline (Quá trình này đọc từ ổ cứng nên chạy rất nhanh, chỉ mất vài mươi giây).
4. Kiểm tra kết quả cuối cùng: Vào thư mục data/ kiểm tra xem file CSV sạch đã được xuất ra thành công chưa.
