import pandas as pd
import yfinance as yf
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

hisseler = ["THYAO.IS", "GARAN.IS", "TUPRS.IS", "MIATK.IS"]
csv_dosyasi = 'gunluk_veriler.csv'

tum_veriler = []
print("Hisseler için veri çekiliyor...")

for hisse_kodu in hisseler:
    try:
        hisse = yf.Ticker(hisse_kodu)
        gunluk_veri = hisse.history( period = "1d")

        if gunluk_veri.empty: 
            print(f"-> '{hisse_kodu}' için veri bulunamadı. Kontrol ediniz.    ")
            continue
        gunluk_veri.reset_index(inplace=True)
        gunluk_veri['Date'] = gunluk_veri['Date'].dt.date

        gunluk_veri['Hisse Kodu'] = hisse_kodu
        secilen_veri = gunluk_veri[['Date', 'Hisse Kodu', 'Open', 'High', 'Low', 'Close', 'Volume']]

        tum_veriler.append(secilen_veri)
        print(f"-> '{hisse_kodu}' verisi başarıyla çekildi.")

    except Exception as e: 
        print(f"{hisse_kodu} işlenirken hata oluştu.")

if not tum_veriler:
    print("Hiçbir hisse senedi için veri çekilmedi. Exit.")
else:
    son_dataframe = pd.concat(tum_veriler)
    dosya_var_mi = os.path.exists(csv_dosyasi)

    print(f"\nVeriler: '{csv_dosyasi}' dosyasına kaydediliyor...")

    try:
        son_dataframe.to_csv(
            csv_dosyasi,
            mode='a',
            header=not dosya_var_mi,
            index=False
        )
        print("Kayıt işlemi başarıyla tamamlandı.")
        print("\n--- Kaydedilen Veri Özeti ---")
        print(pd.read_csv(csv_dosyasi).tail(len(hisseler) + 1))
    
    except Exception as e:
        print(f"CSV dosyasına yazdırılırken hata oluştu: {e}")