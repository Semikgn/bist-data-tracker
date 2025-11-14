import pandas as pd
import yfinance as yf
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

hisseler = ["THYAO.IS", "GARAN.IS", "TUPRS.IS", "MIATK.IS"]
csv_dosyasi = 'gunluk_veriler.csv'
total_period = "2mo"

print(f"Mevcut veritabanı '{csv_dosyasi}' okunuyor...")
current_db = set()

if os.path.exists(csv_dosyasi):
    try:
        df_mevcut = pd.read_csv(csv_dosyasi)
        df_mevcut['Date'] = pd.to_datetime(df_mevcut['Date']).dt.date
        mevcut_veriler_seti = set(zip(df_mevcut['Date'], df_mevcut['Hisse Kodu']))
        print(f"{len(mevcut_veriler_seti)} adet mevcut kayıt bulundu.")
    except pd.errors.EmptyDataError:
        print("Uyarı: CSV dosyası boş.")
    except Exception as e:
        print(f"Mevcut CSV okunurken hata oluştu: {e}")
else:
    print("Mevcut veritabanı bulunamadı, sıfırdan oluşturulacak.")

tum_yeni_veriler = [] 
print(f"Hisseler için son '{total_period}' verisi çekiliyor...")

for hisse_kodu in hisseler:
    try:
        hisse = yf.Ticker(hisse_kodu)
        gunluk_veri = hisse.history(period=total_period) # "2mo" parametresi kullanılıyor

        if gunluk_veri.empty:
            print(f"-> '{hisse_kodu}' için veri bulunamadı.")
            continue

        gunluk_veri.reset_index(inplace=True)
        gunluk_veri['Date'] = gunluk_veri['Date'].dt.date
        gunluk_veri['Hisse Kodu'] = hisse_kodu
        secilen_veri = gunluk_veri[['Date', 'Hisse Kodu', 'Open', 'High', 'Low', 'Close', 'Volume']]

        yeni_satirlar = []
        for _, satir in secilen_veri.iterrows():
            kontrol_anahtari = (satir['Date'], satir['Hisse Kodu'])
            if kontrol_anahtari not in mevcut_veriler_seti:
                yeni_satirlar.append(satir)
        
        if not yeni_satirlar:
            print(f"-> '{hisse_kodu}' için yeni veri bulunamadı (Tüm veriler güncel).")
            continue

        df_yeni = pd.DataFrame(yeni_satirlar)
        tum_yeni_veriler.append(df_yeni)
        print(f"-> '{hisse_kodu}' için {len(df_yeni)} adet YENİ veri bulundu.") 

    except Exception as e:
        print(f"'{hisse_kodu}' işlenirken bir hata oluştu: {e}")

if not tum_yeni_veriler:
    print("\nTüm hisseler için veriler güncel. CSV dosyası değiştirilmedi.")
else:
    son_dataframe = pd.concat(tum_yeni_veriler)
    print(f"\nToplam {len(son_dataframe)} adet yeni veri '{csv_dosyasi}' dosyasına ekleniyor...")
    
    try:
        dosya_var_mi = os.path.exists(csv_dosyasi) and len(mevcut_veriler_seti) > 0
        son_dataframe.to_csv(
            csv_dosyasi,
            mode='a',
            header=not dosya_var_mi,
            index=False
        )
        print("Kayıt işlemi başarıyla tamamlandı.")
        print("\n--- Eklenen Veri Özeti ---")
        print(son_dataframe)

    except Exception as e:
        print(f"CSV dosyasına yazılırken bir hata oluştu: {e}")