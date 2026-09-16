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
with tab1:
    st.subheader("Gợi ý từ khóa từ Google Autocomplete (Real-time)")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        keyword_input = st.text_input("Nhập từ khóa hạt giống (Seed Keyword):", placeholder="ví dụ: thiết kế website")
    with col2:
        lang = st.selectbox("Ngôn ngữ / Thị trường:", ["vi", "en"])
        
    if st.button("🔍 Khám Phá Từ Khóa"):
        if keyword_input:
            with st.spinner("Đang thu thập dữ liệu từ Google..."):
                url = f"http://suggestqueries.google.com/complete/search?client=chrome&hl={lang}&q={keyword_input}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    suggestions = response.json()[1]
                    
                    df_keywords = pd.DataFrame({
                        "Từ khóa gợi ý": suggestions,
                        "Số từ (Words)": [len(k.split()) for k in suggestions],
                        "Số ký tự": [len(k) for k in suggestions],
                        "Phân loại": ["Long-tail (Từ khóa dài)" if len(k.split()) >= 3 else "Short-tail (Từ khóa ngắn)" for k in suggestions]
                    })
                    
                    st.success(f"Tìm thấy {len(suggestions)} từ khóa liên quan!")
                    st.dataframe(df_keywords, use_container_width=True)
                    
                    csv = df_keywords.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 Tải Báo Cáo CSV",
                        data=csv,
                        file_name=f"seo_keywords_{keyword_input}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Không thể lấy dữ liệu từ Google.")
        else:
            st.warning("Vui lòng nhập từ khóa!")

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
