from bs4 import BeautifulSoup

def extract_book_data(html_content):
    """
    Hàm bóc tách nhiều thông tin của các cuốn sách từ trang danh mục.
    Trả về một danh sách các dictionary chứa thông tin chi tiết bề nổi.
    """
    if not html_content:
        return []
        
    soup = BeautifulSoup(html_content, "html.parser")
    books_list = []
    
    # Tìm tất cả các khối bao bọc từng cuốn sách (thẻ li chứa class item-inner)
    # Tiếp cận theo hướng tìm thẻ cha 'item-inner' để đảm bảo gom đúng cụm dữ liệu của cụ thể 1 cuốn sách
    book_items = soup.find_all("div", class_="item-inner")
    
    for item in book_items:
        data = {
            "title": None,
            "link": None,
            "current_price": None,
            "old_price": None,
            "discount": None,
            "rating": None
        }
        
        # 1. Bóc tách Tên sách và Đường link
        name_tag = item.find("h2", class_="product-name-no-ellipsis p-name-list")
        if name_tag:
            a_tag = name_tag.find("a")
            if a_tag:
                data["title"] = a_tag.get("title", "").strip()
                link = a_tag.get("href", "")
                if "?" in link:
                    link = link.split("?")[0]
                data["link"] = link

        # Nếu không lấy được link hoặc tên (khung trống), bỏ qua luôn để tránh rác
        if not data["link"]:
            continue
            
        # 2. Bóc tách Giá bán hiện tại & Phần trăm giảm giá
        special_price_tag = item.find("p", class_="special-price")
        if special_price_tag:
            price_span = special_price_tag.find("span", class_="price")
            if price_span:
                # Lấy text, xóa chữ 'đ', xóa dấu chấm phân cách để sau này ép kiểu INT dễ dàng
                data["current_price"] = price_span.text.replace("đ", "").replace(".", "").strip()
                
            discount_span = special_price_tag.find("span", class_="discount-percent fhs_center_left")
            if discount_span:
                data["discount"] = discount_span.text.replace("-", "").replace("%", "").strip()

        # 3. Bóc tách Giá gốc (Giá bìa)
        old_price_tag = item.find("p", class_="old-price bg-white")
        if old_price_tag:
            old_price_span = old_price_tag.find("span", class_="price")
            if old_price_span:
                data["old_price"] = old_price_span.text.replace("đ", "").replace(".", "").strip()

        # 4. Bóc tách Điểm đánh giá (Rating)
        rating_tag = item.find("div", class_="rating-links")
        if rating_tag:
            data["rating"] = rating_tag.text.strip()
            
        books_list.append(data)
        
    return books_list