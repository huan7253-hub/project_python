import pandas as pd
import re
import unicodedata

# 🛠️ ĐIỀN FILE CSV BẠN MUỐN KIỂM TRA VÀO ĐÂY
FILE_TO_AUDIT = "../data/clean/*.csv"

def run_data_audit():
    print(f"[*] ĐANG KHỞI ĐỘNG KIỂM TOÁN FILE: {FILE_TO_AUDIT}\n")
    try:
        df = pd.read_csv(FILE_TO_AUDIT)
    except Exception as e:
        print(f"[-] Không đọc được file: {e}")
        return

    total_rows = len(df)
    print(f"[📊] Quy mô dữ liệu: {total_rows} dòng sách.\n")
    print("="*50)
    print("🔍 KẾT QUẢ QUÉT 5 LỖI CHÍ MẠNG:")
    print("="*50)

    # 1. Kiểm tra trống hoặc "Đang cập nhật" ở cột mô tả
    missing_desc = df["description"].isna().sum()
    keyword_update = df["description"].fillna("").str.contains("cập nhật|đang cập nhật", case=False).sum()
    print(f"1. Khuyết thiếu nội dung (Description):")
    print(f"   - Số dòng bị trống hoàn toàn (NaN): {missing_desc} dòng")
    print(f"   - Số dòng chứa chữ 'cập nhật/đang cập nhật': {keyword_update} dòng")

    # 2. Kiểm tra rác HTML hoặc ký tự thực thể (&nbsp;, &amp;...)
    html_pattern = re.compile(r"<[^>]+>|&[a-z]+;")
    html_trash_count = df["description"].fillna("").apply(lambda x: 1 if html_pattern.search(str(x)) else 0).sum()
    print(f"\n2. Rác mã code HTML / Thực thể mạng:")
    print(f"   - Số dòng phát hiện dính thẻ HTML ẩn hoặc ký tự &nbsp;...: {html_trash_count} dòng")

    # 3. Kiểm tra lỗi khoảng trắng kép, dấu tab, xuống dòng (\n, \t)
    space_pattern = re.compile(r"\n|\t|\r|  ")
    space_error_count = df["description"].fillna("").apply(lambda x: 1 if space_pattern.search(str(x)) else 0).sum()
    print(f"\n3. Lỗi định dạng khoảng trắng và ngắt dòng:")
    print(f"   - Số dòng dính lỗi xuống dòng đột ngột hoặc khoảng trắng kép: {space_error_count} dòng")

    # 4. Kiểm tra Unicode lệch chuẩn (NFD - Tổ hợp)
    def is_nfd(text):
        if not isinstance(text, str): return False
        return text != unicodedata.normalize('NFC', text)
    
    nfd_count = df["description"].fillna("").apply(lambda x: 1 if is_nfd(str(x)) else 0).sum()
    print(f"\n4. Lỗi bảng mã Tiếng Việt (Unicode NFD/Tổ hợp):")
    print(f"   - Số dòng bị gõ lệch chuẩn (Mắt thấy giống nhưng máy hiểu sai): {nfd_count} dòng")

    # 5. Kiểm tra Emoji và Ký tự lạ gây nhiễu
    # Regex này quét các ký tự nằm ngoài bảng chữ cái VN, số, và dấu câu cơ bản
    emoji_pattern = re.compile(r"[^\w\s,.\-;:!?()\"'áàảãạâấầẩẫậăắằẳẵặéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđĐ]")
    emoji_count = df["description"].fillna("").apply(lambda x: 1 if emoji_pattern.search(str(x)) else 0).sum()
    print(f"\n5. Ký tự lạ / Emoji Marketing:")
    print(f"   - Số dòng dính icon lửa, sao, mũi tên (🚀, 🔥, 🌟...): {emoji_count} dòng")
    print("="*50)

    # In ra một vài dòng dính ký tự lạ làm mẫu để bạn tận mắt nhìn thấy
    if emoji_count > 0:
        print("\n👀 MẪU DÒNG CHỨA KÝ TỰ LẠ ĐỂ BẠN XEM THỬ:")
        sampled = df[df["description"].fillna("").apply(lambda x: bool(emoji_pattern.search(str(x))))].head(2)
        for idx, row in sampled.iterrows():
            print(f"\n[Cuốn: {row['title']}]")
            # Tìm và in ra ký tự lạ đó là gì
            bad_chars = emoji_pattern.findall(str(row['description']))
            print(f" -> Ký tự lạ phát hiện: {list(set(bad_chars))[:10]}")

if __name__ == "__main__":
    run_data_audit()