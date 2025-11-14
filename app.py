import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")

st.title("BIST Veri Takipçisi")
st.write("Bu proje, GitHub Actions ile toplanan BIST verilerini gösterir.")

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

st.sidebar.header("Filtreler")
hisse_listesi = sorted(df['Hisse Kodu'].unique())
secilen_hisse = st.sidebar.selectbox("Hisse Kodu Seçin:", hisse_listesi)

st.header(f"{secilen_hisse} Fiyat Grafiği")

df_filtrelenmis = df[df['Hisse Kodu'] == secilen_hisse].copy()

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
