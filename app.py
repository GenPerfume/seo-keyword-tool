import streamlit as st
import requests
import pandas as pd

# Cấu hình giao diện Trang Web
st.set_page_config(
    page_title="Công Cụ Phân Tích & Kiểm Tra Thứ Hạng SEO",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Hệ Thống Phân Tích & Kiểm Tra Thứ Hạng SEO Chuyên Sâu")
st.markdown("---")

# Sidebar cấu hình API Key
st.sidebar.header("⚙️ Cấu Hình API Dữ Liệu")
st.sidebar.info("Để lấy dữ liệu thứ hạng chính xác từ Google SERP real-time, bạn có thể nhập SerpApi Key.")
serp_api_key = st.sidebar.text_input("SerpAPI Key (Tùy chọn):", type="password")

# Định nghĩa các TAB chức năng
tab1, tab2, tab3 = st.tabs([
    "💡 1. Nghiên Cứu & Gợi Ý Từ Khóa", 
    "📊 2. Gom Nhóm & Phân Tích Intent", 
    "🎯 3. Kiểm Tra Thứ Hạng (SERP Rank Tracker)"
])

# ==========================================
# TAB 1: NGHIÊN CỨU & GỢI Ý TỪ KHÓA
# ==========================================
# ==========================================
# TAB 1: NGHIÊN CỨU & GỢI Ý TỪ KHÓA NÂNG CAO
# ==========================================
with tab1:
    st.subheader("💡 Khám Phá Hàng Trăm Từ Khóa (Alphabet Scraper)")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        keyword_input = st.text_input("Nhập từ khóa hạt giống (Seed Keyword):", placeholder="ví dụ: thiết kế website")
    with col2:
        lang = st.selectbox("Ngôn ngữ:", ["vi", "en"])
        
    if st.button("🚀 Khám Phá Siêu Từ Khóa"):
        if keyword_input:
            with st.spinner("Đang vét dữ liệu từ Google (A-Z)..."):
                all_suggestions = set()
                
                # 1. Lấy gợi ý gốc
                url = f"http://suggestqueries.google.com/complete/search?client=chrome&hl={lang}&q={keyword_input}"
                res = requests.get(url)
                if res.status_code == 200:
                    all_suggestions.update(res.json()[1])
                
                # 2. Chạy vòng lặp từ a -> z để vét sạch từ khóa
                alphabet = ['a', 'b', 'c', 'd', 'e', 'g', 'h', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y']
                for letter in alphabet:
                    query = f"{keyword_input} {letter}"
                    url = f"http://suggestqueries.google.com/complete/search?client=chrome&hl={lang}&q={query}"
                    r = requests.get(url)
                    if r.status_code == 200:
                        all_suggestions.update(r.json()[1])
                
                results_list = list(all_suggestions)
                
                # Tạo bảng hiển thị
                df_keywords = pd.DataFrame({
                    "Từ khóa gợi ý": results_list,
                    "Số từ": [len(k.split()) for k in results_list],
                    "Số ký tự": [len(k) for k in results_list],
                    "Phân loại": ["Long-tail" if len(k.split()) >= 3 else "Short-tail" for k in results_list]
                })
                
                st.success(f"🎉 Đã tìm thấy tổng cộng {len(results_list)} từ khóa chuyên sâu!")
                st.dataframe(df_keywords, use_container_width=True)
                
                # Tải file CSV
                csv = df_keywords.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Tải Báo Cáo CSV", csv, f"keywords_{keyword_input}.csv", "text/csv")
# ==========================================
# TAB 2: GOM NHÓM & PHÂN TÍCH SEARCH INTENT
# ==========================================
with tab2:
    st.subheader("Phân Loại Ý Định Tìm Kiếm (Search Intent)")
    raw_keywords = st.text_area("Dán danh sách từ khóa của bạn vào đây (mỗi từ một dòng):", height=150)
    
    if st.button("📊 Phân Tích Intent"):
        if raw_keywords:
            kw_list = [k.strip() for k in raw_keywords.split('\n') if k.strip()]
            
            intent_data = []
            for kw in kw_list:
                kw_lower = kw.lower()
                if any(w in kw_lower for w in ["mua", "giá", "bảng giá", "bao nhiêu", "shop", "địa chỉ", "đặt hàng"]):
                    intent = "Transactional (Giao dịch)"
                elif any(w in kw_lower for w in ["là gì", "như thế nào", "hướng dẫn", "tại sao", "cách", "mẹo"]):
                    intent = "Informational (Thông tin)"
                elif any(w in kw_lower for w in ["tốt nhất", "so sánh", "top", "review", "đánh giá", "nên mua"]):
                    intent = "Commercial (Thương mại)"
                else:
                    intent = "Navigational (Định hướng)"
                
                intent_data.append({"Từ khóa": kw, "Phân loại Intent": intent})
            
            df_intent = pd.DataFrame(intent_data)
            st.dataframe(df_intent, use_container_width=True)
            
            intent_counts = df_intent["Phân loại Intent"].value_counts()
            st.bar_chart(intent_counts)
        else:
            st.warning("Vui lòng nhập danh sách từ khóa!")

# ==========================================
# TAB 3: KIỂM TRA THỨ HẠNG (RANK TRACKER)
# ==========================================
with tab3:
    st.subheader("Kiểm Tra Thứ Hạng Website Trên Google SERP")
    col_domain, col_target_kw = st.columns(2)
    
    with col_domain:
        target_domain = st.text_input("Domain website (ví dụ: mywebsite.com):")
    with col_target_kw:
        target_kw = st.text_input("Từ khóa cần kiểm tra thứ hạng:")
        
    if st.button("🎯 Kiểm Tra Thứ Hạng"):
        if target_domain and target_kw:
            if serp_api_key:
                with st.spinner("Đang quét kết quả Google SERP real-time..."):
                    try:
                        serp_url = f"https://serpapi.com/search.json?q={target_kw}&hl=vi&gl=vn&api_key={serp_api_key}"
                        res = requests.get(serp_url).json()
                        organic_results = res.get("organic_results", [])
                        
                        rank = None
                        found_url = ""
                        
                        for item in organic_results:
                            if target_domain in item.get("link", ""):
                                rank = item.get("position")
                                found_url = item.get("link")
                                break
                        
                        if rank:
                            st.balloons()
                            st.success(f"🎉 Website của bạn nằm ở **Vị Trí Top {rank}**!")
                            st.info(f"Đường dẫn hiển thị: {found_url}")
                        else:
                            st.error(f"❌ Website không xuất hiện trong Top {len(organic_results)} kết quả đầu tiên.")
                    except Exception as e:
                        st.error(f"Lỗi kết nối API: {e}")
            else:
                st.warning("⚠️ Để kiểm tra thứ hạng chính xác không bị Google chặn IP, vui lòng nhập **SerpAPI Key** ở khung cấu hình bên trái.")
        else:
            st.warning("Vui lòng nhập đầy đủ tên miền và từ khóa!")
