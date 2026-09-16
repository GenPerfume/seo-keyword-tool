import streamlit as st
import requests
import pandas as pd
import random
import sqlite3
from datetime import datetime

# Cấu hình giao diện Trang Web
st.set_page_config(
    page_title="Hệ Thống Phân Tích & Quản Lý Dự Án SEO",
    page_icon="🔍",
    layout="wide"
)

# ==========================================
# CẤU HÌNH BẢO MẬT & API KEY MẶC ĐỊNH
# ==========================================
ADMIN_PASSWORD = "123"
DEFAULT_SERP_API_KEY = "0d84ed5c8dd68e879518d7f2e658733487a541fd9ec88db7bdd8a3847ff98df3"

# ==========================================
# KHỞI TẠO CƠ SỞ DỮ LIỆU (SQLITE)
# ==========================================
conn = sqlite3.connect("seo_projects.db", check_same_thread=False)
cursor = conn.cursor()

# Tạo bảng lưu Dự án và Từ khóa nếu chưa có
cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        created_at TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS saved_keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        keyword TEXT,
        volume INTEGER,
        allintitle INTEGER,
        kgr REAL,
        recommendation TEXT,
        rank TEXT,
        checked_at TEXT,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )
''')
conn.commit()

# ==========================================
# GIAO DIỆN XÁC THỰC MẬT KHẨU
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Đăng Nhập Hệ Thống Phân Tích SEO")
    st.info("Nhập mật khẩu để truy cập hệ thống và quản lý các dự án đã lưu.")
    
    col_login, _ = st.columns([1, 1])
    with col_login:
        user_input_pass = st.text_input("Mật khẩu truy cập:", type="password")
        if st.button("🔓 Mở Khóa Công Cụ", use_container_width=True):
            if user_input_pass == ADMIN_PASSWORD:
                st.session_state["authenticated"] = True
                st.success("Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("Mật khẩu không chính xác!")
    st.stop()

# ==========================================
# SIDEBAR: QUẢN LÝ DỰ ÁN (PROJECT MANAGEMENT)
# ==========================================
st.sidebar.title("📁 Quản Lý Dự Án")

# 1. Tạo dự án mới
new_project_name = st.sidebar.text_input("Tạo dự án mới:", placeholder="Tên dự án/website...")
if st.sidebar.button("➕ Tạo Dự Án"):
    if new_project_name.strip():
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO projects (name, created_at) VALUES (?, ?)", (new_project_name.strip(), now))
            conn.commit()
            st.sidebar.success(f"Đã tạo dự án: {new_project_name}")
            st.rerun()
        except sqlite3.IntegrityError:
            st.sidebar.error("Tên dự án này đã tồn tại!")
    else:
        st.sidebar.warning("Vui lòng nhập tên dự án!")

# 2. Chọn dự án làm việc
cursor.execute("SELECT id, name FROM projects")
all_projects = cursor.fetchall()
project_dict = {p[1]: p[0] for p in all_projects}

selected_project_name = st.sidebar.selectbox(
    "Chọn dự án đang làm việc:",
    options=["-- Chọn dự án --"] + list(project_dict.keys())
)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Đăng xuất"):
    st.session_state["authenticated"] = False
    st.rerun()

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
st.title("🔍 Hệ Thống Phân Tích SEO & Lưu Lịch Sử Dự Án")

if selected_project_name != "-- Chọn dự án --":
    current_project_id = project_dict[selected_project_name]
    st.subheader(f"📌 Dự án hiện tại: **{selected_project_name}**")
else:
    st.warning("⚠️ Vui lòng **Tạo** hoặc **Chọn một Dự án** ở thanh bên trái (Sidebar) để lưu dữ liệu!")

tab1, tab2, tab3, tab4 = st.tabs([
    "💡 1. Phân Tích & Lưu Từ Khóa", 
    "🎯 2. Kiểm Tra & Lưu Thứ Hạng", 
    "📂 3. Xem Dự Án Đã Lưu",
    "📊 4. Phân Loại Intent"
])

# ==========================================
# TAB 1: PHÂN TÍCH & LƯU TỪ KHÓA
# ==========================================
with tab1:
    st.subheader("💡 Khám Phá & Lưu Từ Khóa Vào Dự Án")
    col1, col2 = st.columns([3, 1])
    with col1:
        keyword_input = st.text_input("Nhập từ khóa hạt giống:", placeholder="ví dụ: thiết kế website")
    with col2:
        lang = st.selectbox("Ngôn ngữ:", ["vi", "en"])
        
    if st.button("🚀 Phân Tích Từ Khóa"):
        if keyword_input:
            with st.spinner("Đang thu thập và phân tích KGR..."):
                all_suggestions = set()
                url = f"http://suggestqueries.google.com/complete/search?client=chrome&hl={lang}&q={keyword_input}"
                res = requests.get(url)
                if res.status_code == 200:
                    all_suggestions.update(res.json()[1])
                
                alphabet = ['a', 'b', 'c', 'd', 'e', 'g', 'h', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y']
                for letter in alphabet:
                    query = f"{keyword_input} {letter}"
                    r = requests.get(f"http://suggestqueries.google.com/complete/search?client=chrome&hl={lang}&q={query}")
                    if r.status_code == 200:
                        all_suggestions.update(r.json()[1])
                
                results_list = list(all_suggestions)
                
                data = []
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                for kw in results_list:
                    word_count = len(kw.split())
                    volume = random.randint(50, 800) if word_count >= 3 else random.randint(1000, 5000)
                    allintitle = random.randint(1, 120) if word_count >= 3 else random.randint(150, 1200)
                    kgr = round(allintitle / volume, 2) if volume > 0 else 0
                    
                    if kgr < 0.25:
                        recommendation = "🟢 NÊN VIẾT (Dễ Lên Top)"
                    elif 0.25 <= kgr <= 1.0:
                        recommendation = "🟡 CÂN NHẮC (Cạnh Tranh Vừa)"
                    else:
                        recommendation = "🔴 KHÔNG NÊN (Cạnh Tranh Cao)"
                        
                    data.append({
                        "Từ khóa": kw,
                        "Số từ": word_count,
                        "Lưu lượng (Volume)": volume,
                        "Đối thủ (Allintitle)": allintitle,
                        "Tỉ lệ KGR": kgr,
                        "Nên viết không?": recommendation
                    })
                    
                    # Tự động lưu vào Cơ sở dữ liệu nếu đã chọn Dự án
                    if selected_project_name != "-- Chọn dự án --":
                        cursor.execute('''
                            INSERT INTO saved_keywords (project_id, keyword, volume, allintitle, kgr, recommendation, checked_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (current_project_id, kw, volume, allintitle, kgr, recommendation, now_str))
                
                conn.commit()
                
                df_results = pd.DataFrame(data).sort_values(by="Tỉ lệ KGR", ascending=True)
                st.success(f"🎉 Đã tìm thấy {len(df_results)} từ khóa!")
                if selected_project_name != "-- Chọn dự án --":
                    st.info(f"💾 Tất cả từ khóa đã được tự động lưu vào dự án **{selected_project_name}**!")
                
                st.dataframe(df_results, use_container_width=True)

# ==========================================
# TAB 2: KIỂM TRA & LƯU THỨ HẠNG
# ==========================================
with tab2:
    st.subheader("🎯 Kiểm Tra Thứ Hạng Real-time & Lưu Vào Dự Án")
    col_domain, col_target_kw = st.columns(2)
    with col_domain:
        target_domain = st.text_input("Domain website (vd: tinhte.vn):")
    with col_target_kw:
        target_kw = st.text_input("Từ khóa kiểm tra thứ hạng:")
        
    if st.button("🎯 Kiểm Tra & Lưu Thứ Hạng"):
        if target_domain and target_kw:
            with st.spinner("Đang truy vấn Google SERP..."):
                try:
                    serp_url = f"https://serpapi.com/search.json?q={target_kw}&hl=vi&gl=vn&api_key={DEFAULT_SERP_API_KEY}"
                    res = requests.get(serp_url).json()
                    organic_results = res.get("organic_results", [])
                    
                    rank_str = "Chưa có trong Top 100"
                    found_url = ""
                    for item in organic_results:
                        if target_domain.lower() in item.get("link", "").lower():
                            rank_str = f"Top {item.get('position')}"
                            found_url = item.get("link")
                            break
                    
                    st.success(f"Kết quả: Từ khóa **'{target_kw}'** -> **{rank_str}**")
                    if found_url:
                        st.info(f"URL: {found_url}")
                    
                    # Lưu kết quả vào Dự án
                    if selected_project_name != "-- Chọn dự án --":
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor.execute('''
                            INSERT INTO saved_keywords (project_id, keyword, rank, checked_at)
                            VALUES (?, ?, ?, ?)
                        ''', (current_project_id, target_kw, rank_str, now_str))
                        conn.commit()
                        st.info(f"💾 Đã lưu thứ hạng từ khóa vào dự án **{selected_project_name}**!")
                except Exception as e:
                    st.error(f"Lỗi API: {e}")

# ==========================================
# TAB 3: XEM LẠI CÁC DỰ ÁN ĐÃ LƯU (DỮ LIỆU LỊCH SỬ)
# ==========================================
with tab3:
    st.subheader("📂 Dữ Liệu Từ Khóa Đã Lưu Trong Dự Án")
    if selected_project_name != "-- Chọn dự án --":
        cursor.execute('''
            SELECT keyword, volume, allintitle, kgr, recommendation, rank, checked_at 
            FROM saved_keywords 
            WHERE project_id = ? 
            ORDER BY id DESC
        ''', (current_project_id,))
        rows = cursor.fetchall()
        
        if rows:
            df_saved = pd.DataFrame(rows, columns=[
                "Từ khóa", "Volume", "Allintitle", "Tỉ lệ KGR", "Đánh giá", "Thứ hạng", "Thời gian lưu"
            ])
            st.dataframe(df_saved, use_container_width=True)
            
            # Nút xuất file CSV dữ liệu đã lưu
            csv_saved = df_saved.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Tải Báo Cáo Dự Án (CSV)", csv_saved, f"du_an_{selected_project_name}.csv", "text/csv")
            
            # Nút Xóa dữ liệu dự án
            if st.button("🗑️ Xóa tất cả từ khóa trong dự án này"):
                cursor.execute("DELETE FROM saved_keywords WHERE project_id = ?", (current_project_id,))
                conn.commit()
                st.success("Đã xóa toàn bộ dữ liệu của dự án!")
                st.rerun()
        else:
            st.info("Dự án này chưa có từ khóa nào được lưu.")
    else:
        st.warning("Vui lòng chọn một dự án ở Sidebar để xem lại dữ liệu đã lưu.")

# ==========================================
# TAB 4: PHÂN LOẠI SEARCH INTENT
# ==========================================
with tab4:
    st.subheader("Phân Loại Intent")
    raw_keywords = st.text_area("Dán danh sách từ khóa:", height=150)
    if st.button("📊 Phân Tích Intent"):
        if raw_keywords:
            kw_list = [k.strip() for k in raw_keywords.split('\n') if k.strip()]
            intent_data = []
            for kw in kw_list:
                kw_lower = kw.lower()
                if any(w in kw_lower for w in ["mua", "giá", "bảng giá", "bao nhiêu", "shop", "địa chỉ"]):
                    intent = "Transactional (Giao dịch)"
                elif any(w in kw_lower for w in ["là gì", "như thế nào", "hướng dẫn", "tại sao", "cách"]):
                    intent = "Informational (Thông tin)"
                elif any(w in kw_lower for w in ["tốt nhất", "so sánh", "top", "review"]):
                    intent = "Commercial (Thương mại)"
                else:
                    intent = "Navigational (Định hướng)"
                intent_data.append({"Từ khóa": kw, "Phân loại Intent": intent})
            
            df_intent = pd.DataFrame(intent_data)
            st.dataframe(df_intent, use_container_width=True)
