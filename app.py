"""
app.py  –  Hệ thống Tìm kiếm Lai Fahasa  (Thành viên 3 – Frontend/UI)
=======================================================================
Chạy: streamlit run app.py

Đặt file  fahasa_books_master.csv  cùng thư mục với app.py.
Khi ai_engine.py và mysql_engine.py của nhóm hoàn thiện, thay phần
  "# TODO: gọi engine thật" bằng import + lời gọi hàm tương ứng.
"""

import pandas as pd
import numpy as np
import streamlit as st
import os

# ╔══════════════════════════════════════════════════════════════════╗
# ║  1. TẢI & CACHE DỮ LIỆU THẬT                                    ║
# ╚══════════════════════════════════════════════════════════════════╝

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data/fahasa_books_master.csv")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Đọc CSV, bóc tách danh mục, chuẩn hóa kiểu dữ liệu."""
    df = pd.read_csv(path)

    # Bóc tách cấp-2 từ breadcrumb "Sách tiếng Việt\n/ | Văn học\n/ | ..."
    df["cat_main"] = (
        df["category_path"]
        .str.split(r"\n/ \| ")
        .str[1]
        .str.replace(r"\n/$", "", regex=True)
        .str.strip()
        .fillna("Khác")
    )

    # Điền NaN text
    df["author"]      = df["author"].fillna("Không rõ tác giả")
    df["description"] = df["description"].fillna("")

    # Ép kiểu số
    for col in ("current_price", "old_price"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df["discount_percent"] = (
        pd.to_numeric(df.get("discount_percent", 0), errors="coerce").fillna(0)
    )

    return df


df = load_data(DATA_PATH)

CATEGORIES = ["Tất cả"] + sorted(df["cat_main"].unique().tolist())
MAX_PRICE   = int(df["current_price"].max())       # 9 510 000
CAP_PRICE   = 2_000_000                            # giới hạn slider cho dễ dùng


# ╔══════════════════════════════════════════════════════════════════╗
# ║  2. CẤU HÌNH TRANG                                               ║
# ╚══════════════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title="Fahasa Hybrid Search",
    page_icon="📖",
    layout="wide",
)

st.title("📖 Hệ thống Tìm kiếm Sách Fahasa")
st.caption(
    f"Dataset thật · **{len(df):,} đầu sách** · "
    f"**{df['cat_main'].nunique()} danh mục** · "
    f"Giá từ {df['current_price'].min():,}đ → {MAX_PRICE:,}đ"
)


# ╔══════════════════════════════════════════════════════════════════╗
# ║  3. HÀM HIỂN THỊ LƯỚI SÁCH (Book Cards)                         ║
# ╚══════════════════════════════════════════════════════════════════╝
PLACEHOLDER_IMG = "https://via.placeholder.com/160x220/f0f0f0/333333?text=📚"

def _fmt_title(text: str, max_len: int = 50) -> str:
    text = text or ""
    return text[:max_len] + ("…" if len(text) > max_len else "")

def _fmt_desc(text: str, max_len: int = 130) -> str:
    text = (text or "").strip().replace("\n", " ")
    return text[:max_len] + ("…" if len(text) > max_len else "")

def display_book_grid(books_list: list, cols_per_row: int = 4) -> None:
    """
    books_list : list[dict] – mỗi dict có ít nhất các key:
        id, title, author, current_price, old_price, description, link
    """
    if not books_list:
        st.info("Không tìm thấy sách phù hợp với điều kiện lọc.")
        return

    cols = st.columns(cols_per_row)
    for idx, book in enumerate(books_list):
        with cols[idx % cols_per_row]:
            # ── Ảnh placeholder ──
            st.image(PLACEHOLDER_IMG, use_container_width=True)

            # ── Tiêu đề ──
            st.markdown(f"**{_fmt_title(book.get('title', ''))}**")

            # ── Tác giả ──
            st.caption(f"✍️ {book.get('author', 'Không rõ')}")

            # ── Giá ──
            cur = int(book.get("current_price", 0) or 0)
            old = int(book.get("old_price", 0) or 0)
            if old > cur > 0:
                pct = round((old - cur) / old * 100)
                st.markdown(
                    f"<span style='color:#e74c3c;font-weight:700;font-size:15px'>"
                    f"{cur:,}đ</span>&nbsp;"
                    f"<span style='color:#999;text-decoration:line-through;font-size:12px'>"
                    f"{old:,}đ</span>&nbsp;"
                    f"<span style='background:#e74c3c;color:white;border-radius:4px;"
                    f"padding:1px 5px;font-size:11px'>-{pct}%</span>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<span style='color:#e74c3c;font-weight:700;font-size:15px'>"
                    f"{cur:,}đ</span>",
                    unsafe_allow_html=True,
                )

            # ── Mô tả cắt gọn 3 dòng ──
            st.caption(_fmt_desc(book.get("description", "")))

            # ── Nút mở link Fahasa ──
            st.link_button("🛒 Xem trên Fahasa", book.get("link", "#"))

            st.write("")   # khoảng cách giữa các card


# ╔══════════════════════════════════════════════════════════════════╗
# ║  4. TAB 1 – TÌM KIẾM TỪ KHÓA (MYSQL)                           ║
# ╚══════════════════════════════════════════════════════════════════╝
tab1, tab2 = st.tabs(["🔍 Tìm kiếm thông thường", "🤖 Tìm kiếm bằng AI"])

with tab1:
    col_filter, col_main = st.columns([1, 3], gap="large")

    # ── Sidebar bộ lọc ──
    with col_filter:
        st.subheader("🎯 Bộ lọc")

        category = st.selectbox("📂 Danh mục", CATEGORIES)

        price_range = st.slider(
            "💰 Khoảng giá (đ)",
            min_value=0,
            max_value=CAP_PRICE,
            value=(0, 500_000),
            step=10_000,
            format="%d đ",
        )
        st.caption(f"_(Giá cao nhất trong data: {MAX_PRICE:,}đ)_")

        sort_by = st.radio(
            "↕️ Sắp xếp",
            ["Mặc định", "Giá tăng dần", "Giá giảm dần", "Giảm giá nhiều nhất"],
        )

        max_results = st.slider("📄 Số kết quả hiển thị", 4, 40, 12, 4)

    # ── Khu vực tìm kiếm & kết quả ──
    with col_main:
        search_query = st.text_input(
            "🔎 Nhập tên sách hoặc tác giả…",
            placeholder="Ví dụ: Đắc Nhân Tâm, Nguyễn Nhật Ánh, Harry Potter…",
        )

        # ── Lọc dữ liệu (Pandas mock mysql_engine) ──
        result = df.copy()

        if search_query.strip():
            kw = search_query.strip().lower()
            result = result[
                result["title"].str.lower().str.contains(kw, na=False)
                | result["author"].str.lower().str.contains(kw, na=False)
            ]

        if category != "Tất cả":
            result = result[result["cat_main"] == category]

        result = result[
            (result["current_price"] >= price_range[0])
            & (result["current_price"] <= price_range[1])
        ]

        if sort_by == "Giá tăng dần":
            result = result.sort_values("current_price", ascending=True)
        elif sort_by == "Giá giảm dần":
            result = result.sort_values("current_price", ascending=False)
        elif sort_by == "Giảm giá nhiều nhất":
            result = result.sort_values("discount_percent", ascending=False)

        # ── Hiển thị kết quả ──
        total = len(result)
        if search_query.strip() or category != "Tất cả":
            badge = f"**{total:,} kết quả**"
            if total == 0:
                st.warning(f"{badge} — Thử từ khóa khác hoặc mở rộng bộ lọc.")
            else:
                st.success(
                    f"{badge} _(hiển thị {min(total, max_results)})_"
                    + (" — Dùng Bộ lọc giá để thu hẹp" if total > 50 else "")
                )
        else:
            # Chưa tìm gì → gợi ý random
            st.info("Nhập từ khóa hoặc chọn danh mục để tìm sách.")
            result = df.sample(min(max_results, len(df)), random_state=42)

        # TODO: Thay bằng lời gọi mysql_engine.search_by_keyword_and_filter(...)
        books_to_show = result.head(max_results).to_dict("records")
        display_book_grid(books_to_show)


# ╔══════════════════════════════════════════════════════════════════╗
# ║  5. TAB 2 – TÌM KIẾM AI (CHROMADB)                              ║
# ╚══════════════════════════════════════════════════════════════════╝
with tab2:
    st.info(
        "🚧 **Module AI** (ChromaDB + BAAI/bge-m3) đang được **Thành viên 1** phát triển.\n\n"
        "Giao diện đã sẵn sàng — hiện dùng **Mock Data** để kiểm thử layout.",
        icon="ℹ️",
    )

    user_idea = st.text_area(
        "💡 Bạn đang tìm sách về chủ đề gì? (viết tự do)",
        placeholder=(
            "Ví dụ: Tôi muốn đọc một cuốn sách giúp tôi vượt qua áp lực công việc "
            "và tìm lại sự cân bằng trong cuộc sống…"
        ),
        height=130,
    )

    col_a, col_b = st.columns([1, 5])
    with col_a:
        top_k = st.selectbox("Top K kết quả", [4, 8, 12, 20], index=1)

    if st.button("🤖 AI Tìm kiếm", type="primary"):
        if not user_idea.strip():
            st.warning("Vui lòng nhập mô tả.")
        else:
            with st.spinner("Đang quét không gian Vector..."):
            # 1. Gọi hàm của Bạn (Lead) để bốc ra list ID số nguyên (~0.2 giây)
                from engines.ai_engine import search_by_ai
                matched_ids = search_by_ai(user_idea, top_k=top_k)
            
            # 2. Gọi hàm của Thằng làm SQL để từ list ID bốc ra list dict thông tin sách
            # from engines.mysql_engine import fetch_books_by_ids
            # books_ai = mysql_engine.fetch_books_by_ids(matched_ids)
            
            # Khúc này tạm thời dùng Pandas của nó để map từ ID ra thông tin sách phục vụ test AI trước:
            books_ai = df[df["id"].isin(matched_ids)].to_dict("records")

        st.success(f"AI tìm thấy {len(books_ai)} cuốn sách phù hợp thực tế!")
        display_book_grid(books_ai)


# ╔══════════════════════════════════════════════════════════════════╗
# ║  6. BOTTOM – SÁCH GIẢM GIÁ NHIỀU NHẤT                          ║
# ╚══════════════════════════════════════════════════════════════════╝
st.divider()
st.subheader("🔥 Đang giảm giá mạnh nhất")
hot = (
    df[df["discount_percent"] >= 20]
    .nlargest(8, "discount_percent")
    .to_dict("records")
)
display_book_grid(hot, cols_per_row=4)
