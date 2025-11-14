import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")

st.title("BIST Veri Takipçisi")
st.write("Bu proje, GitHub Actions ile toplanan BIST verilerini gösterir.")

# Veri çek
try:
    csv_dosyasi_adi = 'gunluk_veriler.csv'
    df = pd.read_csv(csv_dosyasi_adi)
    df['Date'] = pd.to_datetime(df['Date'])
except FileNotFoundError:
    st.error(f"HATA: '{csv_dosyasi_adi}' dosyası bulunamadı. Lütfen V1 otomasyonunun çalışmasını bekleyin.")
    st.stop()
except pd.errors.EmptyDataError:
    st.warning("Veritabanı ('gunluk_veriler.csv') şu anda boş. Lütfen V1 otomasyonunun çalışmasını bekleyin.")
    st.stop()

# --- 1. Hafıza (Session State) ve URL Parametresi ---
hisse_listesi = sorted(df['Hisse Kodu'].unique())

# URL'den 'hisse' parametresini oku (Tıklama mekanizması)
query_params = st.query_params
if "hisse" in query_params:
    # URL'de bir hisse varsa, hafızadaki 'secilen_hisse'yi GÜNCELLE
    st.session_state.secilen_hisse = query_params["hisse"]
    # URL'i temizle (sayfanın normal görünmesi için)
    st.query_params.clear()

# Eğer hafızada 'secilen_hisse' hala yoksa (ilk açılış)
if 'secilen_hisse' not in st.session_state:
    if hisse_listesi:
        st.session_state.secilen_hisse = hisse_listesi[0]
    else:
        st.session_state.secilen_hisse = None

# --- 2. Kenar Çubuğu (Sidebar) Mantığı (V3.0 - HTML/CSS) ---
st.sidebar.header("Hisse Listesi")
if not hisse_listesi:
    st.sidebar.warning("Veritabanında hiç hisse bulunamadı.")
else:
    # Sütun Başlıkları (tıklanabilir değil)
    col1, col2, col3 = st.sidebar.columns([3, 2, 2]) 
    with col1: st.caption("Hisse")
    with col2: st.caption("Son Fiyat")
    with col3: st.caption("Değişim")
    st.sidebar.divider() 

    # Her hisse için TIKLANABİLİR HTML hücresi oluştur
    for hisse in hisse_listesi:
        hisse_data = df[df['Hisse Kodu'] == hisse].sort_values('Date')
        
        last_price = 0.0
        delta_str = "---"
        color = "gray"
        
        if len(hisse_data) >= 2:
            last_price = hisse_data.iloc[-1]['Close']
            prev_price = hisse_data.iloc[-2]['Close']
            change_pct = ((last_price - prev_price) / prev_price) * 100
            delta_str = f"{change_pct:+.2f}%" 
            color = "green" if change_pct > 0 else "red" if change_pct < 0 else "gray"
        elif len(hisse_data) == 1:
            last_price = hisse_data.iloc[-1]['Close']

        # --- YENİ V3.0 TIKLANABİLİR HÜCRE ---
        
        # O an seçili olan hisse ise, arka planı vurgula
        is_selected = (hisse == st.session_state.secilen_hisse)
        bg_color = "#2b3139" if is_selected else "transparent" # Vurgu rengi
        
        st.markdown(f"""
        <a href="?hisse={hisse}" target="_self" style="text-decoration: none;">
            <div style="display:flex; justify-content:space-between; align-items:center; padding: 5px 10px; border-radius: 5px; background-color: {bg_color}; margin-bottom: 5px;">
                
                <span style="color: white; font-weight: 500; flex: 3;">{hisse}</span>
                
                <span style="color: white; text-align: right; flex: 2; font-size: 0.9em;">{last_price:.2f}</span>
                
                <span style="color: {color}; text-align: right; flex: 2; font-size: 0.9em; font-weight: 500;">{delta_str}</span>
            </div>
        </a>
        """, unsafe_allow_html=True)
        
# Grafik ve Tablo
secilen_hisse_kodu = st.session_state.secilen_hisse

if secilen_hisse_kodu:
    st.header(f"{secilen_hisse_kodu} Fiyat Grafiği")
    df_filtrelenmis = df[df['Hisse Kodu'] == secilen_hisse_kodu].copy()

    if df_filtrelenmis.empty:
        st.warning("Bu hisse için veri bulunamadı.")
    else:
        df_recent = df_filtrelenmis.tail(30) 
        x_domain_min = df_recent['Date'].min()
        x_domain_max = df_recent['Date'].max()
        x_padding = (x_domain_max - x_domain_min) * 0.05 
        x_scale = alt.Scale(domain=[x_domain_min - x_padding, x_domain_max + x_padding])

        y_min = df_recent['Close'].min()
        y_max = df_recent['Close'].max()
        y_padding = (y_max - y_min) * 0.15 
        y_domain_min = max(0, y_min - y_padding) 
        y_domain_max = y_max + y_padding
        y_scale = alt.Scale(domain=[y_domain_min, y_domain_max])

        # ------- Graph and Volume Graph Part ------
        
        base = alt.Chart(df_filtrelenmis).encode(
            # X EKSENİ ETİKETLERİ GERİ GELDİ (axis=None kaldırıldı)
            x=alt.X('Date:T', title='Tarih', scale=x_scale), 
            y=alt.Y('Close', title='Kapanış Fiyatı (TL)', scale=y_scale),
            tooltip=['Date', 'Hisse Kodu', 'Open', 'High', 'Low', 'Close', 'Volume']
        )
        line = base.mark_line(color='#1f77b4')
        points = base.mark_circle(size=60, color='#ff7f0e')
        price_chart = (line + points).interactive()
        
        st.altair_chart(price_chart, use_container_width=True)

        # --- Ham Veri Tablosu ---
        st.subheader("Son 7 Gün Tablosu")
        df_tablo = df_filtrelenmis.set_index('Date')
        st.dataframe(df_tablo.tail(7))

        # --- Hacim Grafiği ---
        st.subheader("Hacim (Volume) Grafiği")
        
        # Renk hesaplamasını yap
        df_filtrelenmis['color'] = df_filtrelenmis.apply(
            lambda row: 'green' if row['Close'] >= row['Open'] else 'red', 
            axis=1
        )
        
        volume_chart = alt.Chart(df_filtrelenmis).mark_bar().encode(
            x=alt.X('Date:T', title='Tarih', scale=x_scale),
            y=alt.Y('Volume', title='Hacim'),
            color=alt.Color('color', scale={'domain': ['green', 'red'], 'range': ['#2ca02c', '#d62728']}, legend=None),
            tooltip=['Date', 'Volume', 'Close', 'Open']
        ).interactive()

        st.altair_chart(volume_chart, use_container_width=True)
else:
    st.error("Veritabanında görüntülenecek hiç hisse yok.")
