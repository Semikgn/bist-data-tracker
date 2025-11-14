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

# Session State
hisse_listesi = sorted(df['Hisse Kodu'].unique())

if 'secilen_hisse' not in st.session_state:
    st.session_state.secilen_hisse = hisse_listesi[0]

st.sidebar.header("Hisse Listesi")

# Hafızayı güncelleyecek yardımcı fonksiyon
def set_hisse(hisse_kodu):
    st.session_state.secilen_hisse = hisse_kodu

# Her hisse için "Hücre" oluştur
for hisse in hisse_listesi:
    # O hisseye ait veriyi al ve tarihe göre sırala
    hisse_data = df[df['Hisse Kodu'] == hisse].sort_values('Date')
    
    # Fiyat ve değişim hesaplaması yap
    if len(hisse_data) < 2:
        # Eğer yeterli veri yoksa (1 günden az)x
        last_price = hisse_data.iloc[-1]['Close'] if len(hisse_data) == 1 else 0
        delta_str = None # Değişim hesaplanamaz
        change_pct = 0
    else:
        last_price = hisse_data.iloc[-1]['Close']
        prev_price = hisse_data.iloc[-2]['Close']
        change_pct = ((last_price - prev_price) / prev_price) * 100
        delta_str = f"{change_pct:.2f}%"

    # Difference in price increase/decrease
    st.sidebar.metric(
        label=hisse, 
        value=f"{last_price:.2f} TL", # Son Fiyat
        delta=delta_str 
    )
    
    # Click button -> update state
    st.sidebar.button(
        "Grafiği Görüntüle", 
        key=f"btn_{hisse}", 
        on_click=set_hisse, 
        args=(hisse,), 
        use_container_width=True 
    )    
    st.sidebar.divider()

# Grafik ve Tablo
secilen_hisse_kodu = st.session_state.secilen_hisse

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

    base = alt.Chart(df_filtrelenmis).encode(
        x=alt.X('Date:T', title='Tarih', scale=x_scale),
        y=alt.Y('Close', title='Kapanış Fiyatı (TL)', scale=y_scale),
        tooltip=['Date', 'Hisse Kodu', 'Open', 'High', 'Low', 'Close', 'Volume']
    )

    line = base.mark_line(color='#1f77b4')
    points = base.mark_circle(size=60, color='#ff7f0e')
    chart = (line + points).interactive()
    st.altair_chart(chart, use_container_width=True)

st.subheader("Ham Veri Tablosu (Son 50 Gün)")
df_tablo = df_filtrelenmis.set_index('Date')
st.dataframe(df_tablo.tail(50))
