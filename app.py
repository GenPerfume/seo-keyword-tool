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
