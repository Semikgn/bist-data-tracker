import streamlit as st 
import pandas as pd

st.set_page_config(layout = "wide")

st.title("Bist Veri Takipçisi V2")
st.write("Bist verileriyle görselleştirme ve analiz tahmin operayonlarını geliştirmekteyiz...")

try:
    csv_dosyasi = "gunluk_veriler.csv"
    df = pd.read_csv(csv_dosyasi)
    df['Date'] = pd.to_datetime(df['Date'])

except FileNotFoundError:
    st.error(f"Hata: '{csv_dosyasi}' bulunamadı. ")
    st.stop()

# --- Arayüz Tasarımı ---
st.sidebar.header("Filtreler")
hisseler = df['Hisse Kodu'].unique()
secilen_hisse = st.sidebar.selectbox("Hisse kodu seçin: ", hisseler)

st.header(f"{secilen_hisse} Fiyat Grafiği")

df_filtrelenmis = df[df['Hisse Kodu'] == secilen_hisse].copy()

# Temel (base) grafiği oluştur
base = alt.Chart(df_filtrelenmis).encode(

    x=alt.X('Date:T', title='Tarih'),    
    y=alt.Y('Close', title='Kapanış Fiyatı (TL)', scale=alt.Scale(zero=True)),
    
    tooltip=['Date', 'Hisse Kodu', 'Open', 'High', 'Low', 'Close', 'Volume']
)

line = base.mark_line(color='#1f77b4')
points = base.mark_circle(size=60, color='#ff7f0e')

chart = (line + points).interactive()
st.altair_chart(chart, use_container_width=True)

st.subheader("Ham Veri Tablosu (Son 50 Gün)")
df_tablo = df_filtrelenmis.set_index('Date')
st.dataframe(df_tablo.tail(50))